# -*- coding: utf-8 -*-

import fedmsg.consumers
import koji

from autocloud.utils import get_image_url, produce_jobs, get_image_name
import autocloud

import logging
log = logging.getLogger("fedmsg")

DEBUG = autocloud.DEBUG


class AutoCloudConsumer(fedmsg.consumers.FedmsgConsumer):

    if DEBUG:
        topic = [
            'org.fedoraproject.dev.__main__.pungi.compose.status.change'
        ]

    else:
        topic = [
            'org.fedoraproject.prod.pungi.compose.status.change'
        ]

    config_key = 'autocloud.consumer.enabled'

    def __init__(self, *args, **kwargs):
        super(AutoCloudConsumer, self).__init__(*args, **kwargs)

    def consume(self, msg):
        """ This is called when we receive a message matching the topic. """

        builds = list()  # These will be the Koji build IDs to upload, if any.
        log.info('Received %r %r' % (msg['topic'], msg['body']['msg_id']))

        STATUS_F = ('FINISHED_INCOMPLETE', 'FINISHED',)
        VARIANTS_F = ('Cloud', 'Server')

        images = []

        if msg['body']['status'] in STATUS_F:
            location = msg['body']['location']
            json_metadata = '{}/metadata/images.json'.format(location)

            resp = requests.get(json_metadata)
            compose_images_json = getattr(resp, 'json', False)

            if compose_images_json:
                compose_images_json = compose_images_json()

                compose_images = compose_images_json['payload']['images']
                compose_details = compose_images_json['payload']['compose']

                for variant in VARIANTS_F:
                    for arch, payload in compose_images[variant].iteritems():
                        for item in payload:
                            relative_path = item['path']
                            absolute_path = '{}/{}'.format(location,
                                                           relative_path)
                            item.update({
                                'compose': compose_details,
                                'absolute_path': absolute_path,
                            })
                            images.append(item)

        num_images = len(images)
        for pos, image in enumerate(images):
            image.update({'pos': (pos+1, num_images)})

        produce_jobs(images)
