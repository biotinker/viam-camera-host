# viam-camera-host
A Viam module for hosting the image returned by a Viam camera via http

This module will start a simple HTTP server on the designated port, and will host a temp directory whose contents will be an image named `current.jpg`. This image will be updated with the current output of a Viam camera at a user defined cadence (default 5 seconds).

## Setup

Add the module to your robot from the Viam registry. The component may then be added to your configuration as follows

```
  ...
  "components": [
    ...,
    {
      "name": "componentNameHere",
      "model": "biotinker:generic:camerahost",
      "type": "generic",
      "namespace": "rdk",
      "attributes": {
        "port": 9003,
        "camera": "cameraName"
      },
      "depends_on": [
        "cameraName"
      ],
    },
    ...,
  ],
  ...
```

The `camera` field must be the name of the camera to host and is required. The `port` field is the port on which the http server should run an is required. The `refresh` field is optional and specifies the number of seconds between image updates. If absent, or less than or equal to 0, will default to 5.
