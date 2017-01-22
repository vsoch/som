# SOM

School of Medicine Python Tools

**under development**

Starting some very basic Python based tools for working with / moving SOM data, likely to and from Google Cloud. 

## Installation

      pip install git+git://github.com/radinformatics/som-tools.git


For official releases, eventually will be:


      pip install som


## Use Cases

### Convert Dicom to Nifti

See the [full example](examples/dicom2nifti.py). Briefly, to save to a custom output folder:


	output_folder = '/home/vanessa/Desktop'
	outfiles = dicom2nifti(folders,output_folder)

	DEBUG:som:Found 1 directories with dicom.
	DEBUG:som:First dicom found with dimension 512 by 512, using as standard.
	INFO:som:Saving /home/vanessa/Desktop/ST-2034619995971856625.nii.gz
	DEBUG:som:Found 1 directories with dicom.
	DEBUG:som:First dicom found with dimension 512 by 512, using as standard.
	INFO:som:Saving /home/vanessa/Desktop/ST-9134992622373037207.nii.gz
	DEBUG:som:Found 1 directories with dicom.
	DEBUG:som:First dicom found with dimension 512 by 512, using as standard.
	INFO:som:Saving /home/vanessa/Desktop/ST-6141651738472648472.nii.gz



