# Oemer (End-to-end OMR)

End-to-end Optical Music Recognition system build on deep learning models and machine learning techniques.
Default to use **Onnxruntime** for model inference. If you want to use **tensorflow** for the inference,
run `export INFERENCE_WITH_TF=true` and make sure there is TF installed.

![](figures/tabi_mix.jpg)

https://user-images.githubusercontent.com/24308057/136168551-2e705c2d-8cf5-4063-826f-0e179f54c772.mp4



## Quick Start
``` bash
git clone https://github.com/meteo-team/oemer
cd oemer
python setup.py install
oemer --help
```

Or download the built wheel file from the release and install
``` bash
# Go to the release page and download the .whl file from
# the assets.

# Replace the <version> to the correct version.
pip install Oemer-<version>-py3-none-any.whl
```

## Packaging
``` bash
python setup.py bdist_wheel

# Install from the wheel file
pip install dist/Oemer-<version>-py3-none-any.whl
```

## Change log level
``` bash
# Available options: debug, info, warn, warning, error, crtical
export LOG_LEVEL=debug
```


## Technical Details

This section describes the detail techniques for solving the OMR problem. The overall flow can also be found in [oemer/ete.py](https://github.com/meteo-team/oemer/blob/main/oemer/ete.py), which is also the entrypoint for `oemer` command.

### Model Prediction
Oemer first predicts different informations with two image semantic segmentation models: one for
predicting stafflines and all other symbols; and second model for more detailed symbol informations,
including noteheads, clefs, stems, rests, sharp, flat, natural.


<p align='center'>
    <img width="70%" src="figures/tabi_model1.jpg">
    <p align='center'>Model one for predicting stafflines (red) and all other symbols (blue).</p>
</p>
<p align='center'>
    <img width="70%" src="figures/tabi_model2.jpg">
    <p align='center'>Model two for predicting noteheads (green), clefs/sharp/flat/natural (pink), and stems/rests (blue).</p>
</p>

### Dewarping

Before proceed to recognizing the symbols, one may need to deskew the photo first since 
the later process assumes the stafflines are all horizontally aligned and the position 
of noteheads, rests and all other things are all depends on this assumption.

For the dewarping, there can be summarized to six steps as shown in the below figure.

<p align='center'>
    <img width="100%" src="figures/dewarp_steps.png">
    <p align='center'>Steps to dewarp the curved image.</p>
</p>


The dewarping map will be apply to all the predicted informations by the two models.

### Staffline Extraction

After dewarping, stafflines will be parsed. This step plays the most important role,
as this is the foundation to all the later steps. Ths most important information is 
`unit_size`, which is the interval between stafflines. It's obvious that all the sizes,
distance-related information in a music score all relate to the interval, or gap, of stafflines.

The stafflines are processed part-by-part horizontally, as shown below:

<p align='center'>
    <img width="50%" src="figures/staffs.jpg">
</p>

For each part, the algorithm finds the lines by accumulating positive pixels by rows.
After summarizing the counts for each row, we get the following statistics:

<p align='center'>
    <img width="50%" src="figures/staffline_peaks.png">
</p>

The algorithm then picks all the peaks and applies additional rules to filter out false positive peaks.
The final picked true positive peaks (stafflines) are marked with red dots.

Another important information is **tracks** and **groups**. For a conventional piano score, there are
two tracks, for left and right hand, respectively, and forms a group. For this information,
the algorithm *foresees* the symbols predictions and parse the barlines to infer possible
track numbers.

After extraction, the informations are stored into list of `Staff` instances. Example 
`Staff` instance representation is as follow:

``` bash
# Example instance of oemer.staffline_extraction.Staff
Staff(
    Lines: 5  # Contains 5 stafflines.
    Center: 1835.3095048449181  # Y-center of this block of staff.
    Upper bound: 1806  # Upper bound of this block of staff (originated from left-top corner).
    Lower bound: 1865  # Lower bound of this block of staff (originated from left-top corner).
    Unit size: 14.282656749749265  # Average interval of stafflines.
    Track: 1  # For two-handed piano score, there are two tracks.
    Group: 3  # For two-handed piano score, two tracks are grouped into one.
    Is interpolation: False  # Is this block of staff information interpolated.
    Slope: -0.0005315575840202954  # Estimated slope
)
```

### Notehead Extraction

The next step is to extract noteheads, which is the second important information to be parsed.

Steps to extract noteheads are breifly illustrated in the following figure:

<p align='center'>
    <img width="100%" src="figures/notehead.png">
</p>


One of the output channel of the second model predicts the noteheads map, as can be seen in the
top-middle image. The algorithm then pre-process it with morphing to refine the information.
Worth noticing here is that we force the model to predict 'hollow' notes to be solid noteheads,
which thus the information won't be eliminated by the morphing.

Next, the algorithm detects the bounding boxes of each noteheads. Since the noteheads could
overlap with each other, the initial detection could thus contain more than one noteheads. 
To deal with such situation, the algorithm integrate the information `unit_size` to approximate
how many noteheads are actually there, in both horizontal and vertical direction. The result
is shown in the bottom-left figure.

As we force the model to predict both half and whole notes to be solid noteheads, we need to
setup rules to decide whether they are actually half or whole notes. This could be done by
simply compare the region coverage rate between the prediction and the original image.
The result is shown in the bottom-middle figure.

Finally, the last thing to be parsed is the position of noteheads on stafflines. The origin
starts from the bottom line space with (D4 for treble clef, and F3 for bass clef) index 0.
There could be negative numbers as well. In this step, noteheads are also being assigned with
track and group number, indicating which stave they belong to. The bottom-right figure shows
the result.


``` bash
# Example instance of oemer.notehead_extraction.NoteHead
Notehead 12 (  # The number refers to note ID
    Points: 123  # Number of pixels for this notehead.
    Bounding box: [649 402 669 419]
    Stem up: None  # Direction of the stem, will be infered in later steps.
    Track: 1
    Group: 0
    Pitch: None  # Actual pitch in MIDI number, will be infered in later steps.
    Dot: False  # Whether there is dot for this note.
    Label: NoteType.HALF_OR_WHOLE  # Initial guess of the rhythm type.
    Staff line pos: 4  # Position on stafflines. Counting from D4 for treble clef.
    Is valid: True  # Flag for marking if the note is valid.
    Note group ID: None  # Note group ID this note belong to. Will be infered in later steps.
    Sharp/Flat/Natural: None  # Accidental type of this note. Will be infered in later steps.
)

```

### Note Group Extraction

This step groups individual noteheads into chords that should be played at the same time.

A quick snippet of the final result is shown below:

<p align='center'>
    <img width="70%" src="figures/note_group.png">
</p>

The first step is to group the noteheads according mainly to their distance vertically, and then
the overlapping and a small-allowed distance horizontally.

After the initial grouping, the next is to parse the stem direction and further use this
information to refine the grouping results. Since there could be noteheads that are vertically
very close, but have different directions of stems. This indicates that there are two
different melody lines happening at the same time. This is specifically being considered
in `oemer` and taken care of over all the system.

``` bash
# Example instance of oemer.note_group_extraction.NoteGroup
Note Group No. 0 / Group: 0 / Track: 0 :(
    Note count: 1
    Stem up: True
    Has stem: True
)
```
