from typing import ClassVar, Mapping, Sequence, Any, Dict, Optional, cast
from typing_extensions import Self

from viam.module.types import Reconfigurable
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName, Vector3
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily

from viam.components.camera import Camera
from viam.components.generic import Generic
from viam.logging import getLogger
from viam.utils import struct_to_dict, dict_to_struct, ValueTypes

from http.server import HTTPServer, SimpleHTTPRequestHandler

import time
import asyncio
import subprocess
import os
import socket
import threading
import socketserver
import tempfile
import functools

LOGGER = getLogger(__name__)

class CAMHOST(Generic, Reconfigurable):
    MODEL: ClassVar[Model] = Model(ModelFamily("biotinker", "generic"), "camerahost")
    running = False

    # Constructor
    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        camhost = cls(config.name)
        camhost.reconfigure(config, dependencies)
        return camhost

    # Validates JSON Configuration
    @classmethod
    def validate(cls, config: ComponentConfig):
        cam_name = config.attributes.fields["camera"].string_value
        if cam_name == "":
            raise Exception("A camera must be defined")
        port = config.attributes.fields["port"].number_value
        if port == 0:
            raise Exception("A port must be defined")
        return

    # Handles attribute reconfiguration
    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        cam_name = config.attributes.fields["camera"].string_value
        port = int(config.attributes.fields["port"].number_value)
        
        refresh = config.attributes.fields["refresh"].number_value
        if refresh <= 0:
            refresh = 5
        
        cam = dependencies[Camera.get_resource_name(cam_name)]
        self.cam = cam
        self.dirpath = tempfile.mkdtemp()
        self.refresh = refresh
        if self.running:
            LOGGER.info("Shutting server down")
            self.server.shutdown()
            LOGGER.info("Shut server down")
        else:
            LOGGER.info("Starting image thread")
            self.start_img_thread()
            LOGGER.info("Started")
        LOGGER.info("Starting server")
        Handler = functools.partial(SimpleHTTPRequestHandler, directory=self.dirpath)
        self.server = HTTPServer(('0.0.0.0', port), Handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        LOGGER.info("Started")
        # Exit the server thread when the main thread terminates
        self.server_thread.start()
        self.running = True

        return

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
        return {}

    def thread_run(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.next_image())

    def start_img_thread(self):
        self.thread = threading.Thread(target=self.thread_run())
        self.thread.start()

    async def next_image(self):
        os.chdir(self.dirpath)
        while(1):
            await asyncio.sleep(self.refresh)
            try:
                image = await self.cam.get_image()
                image.save(self.dirpath + "/next.jpg")
                os.replace(self.dirpath + "/next.jpg", self.dirpath + "/current.jpg")
            except Exception as e:
                LOGGER.error("failed to get and save image: {}".format(e))
                continue
