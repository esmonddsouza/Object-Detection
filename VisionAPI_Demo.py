import os
import io
from google.cloud import vision
import json
from google.cloud.vision import types

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'level-choir-270012-9c065919be6c.json'


def detect_objects(image):
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    objects = client.object_localization(image=image).localized_object_annotations
    print(objects)
    return objects


def max_value(left, center, right):
    max = 'left'
    max_value = left
    if right > max_value:
        max = 'right'
        max_value = right
    if center > max_value:
        max = 'center'
        max_value = center
    return max


def locate_object(objects):
    objects_detected = []
    if len(objects) == 0:
        print("Sorry, couldn't detect the object")
    else:
        for object in objects:
            if object.score > 0.25:
                x_vertices = set()
                y_vertices = set()
                left = 0.0
                center = 0.0
                right = 0.0
                for vertex in object.bounding_poly.normalized_vertices:
                    x_vertices.add(round(vertex.x, 4))
                    y_vertices.add(round(vertex.y, 4))
                x_vertices = sorted(x_vertices)
                y_vertices = sorted(y_vertices)
                object_width = x_vertices[1] - x_vertices[0]
                object_height = y_vertices[1] - y_vertices[0]

                if x_vertices[0] <= 0.3333:
                    if x_vertices[1] < 0.3333:
                        left = object_width
                    elif x_vertices[1] < 0.6666:
                        left = 0.3333 - x_vertices[0]
                        center = x_vertices[1] - 0.3333
                    elif x_vertices[1] <= 1:
                        left = 0.3333 - x_vertices[0]
                        center = 0.3333
                        right = x_vertices[1] - 0.6666

                if 0.6666 >= x_vertices[0] > 0.3333:
                    if x_vertices[1] < 0.6666:
                        center = object_width
                    elif x_vertices[1] <= 1:
                        center = 0.6666 - x_vertices[0]
                        right = x_vertices[1] - 0.6666

                if x_vertices[0] > 0.6666:
                    right = object_width

                moving_direction = ''
                steps = 0

                if max_value(left, center, right) == 'right':
                    if center == 0:
                        moving_direction = 'left'
                        steps = 0
                    elif center == 0.3333 and left > 0:
                        moving_direction = 'left'
                        steps = 2
                    else:
                        moving_direction = 'left'
                        steps = 1

                if max_value(left, center, right) == 'left':
                    if center == 0:
                        moving_direction = 'right'
                        steps = 0
                    if center == 0.3333 and right > 0:
                        moving_direction = 'right'
                        steps = 2
                    else:
                        moving_direction = 'right'
                        steps = 1

                if max_value(left, center, right) == 'center':
                    if right > left:
                        moving_direction = 'left'
                        if left == 0:
                            steps = 1
                        else:
                            steps = 2
                    if left > right:
                        moving_direction = 'right'
                        if right == 0:
                            steps = 1
                        else:
                            steps = 2

                print(object.name, '\n', 'Confidence -', object.score, '\n', 'Position:',
                      max_value(left, center, right), '\n', 'Moving direction -', moving_direction, '\n',
                      'Steps -', steps, '\n', )
                object_details = ObjectDetails(object.name, max_value(left, center, right), moving_direction, steps, left, right, center);
                objects_detected.append(object_details)
    return objects_detected


def final_directions(objects_detected):
    if len(objects_detected) == 1:
        output_object = Output(objects_detected[0].moving_direction, objects_detected[0].moving_steps)
    else:
        directions = set()
        positions = set()
        moving_steps = set()
        right_values = set()
        left_values = set()
        center_values = set()
        objects = []
        final_moving_direction = ''
        final_steps = ''
        for detected_object in objects_detected:
            directions.add(detected_object.moving_direction)
            positions.add(detected_object.object_position)
            moving_steps.add(detected_object.moving_steps)
            left_values.add(detected_object.left)
            center_values.add(detected_object.center)
            right_values.add(detected_object.right)
            objects.append(detected_object.object_name)
        print(positions, ' ', directions)
        if len(positions) == 3:
            print(max(left_values), ' ', max(right_values))
            if max(left_values) < max(right_values) and max(left_values) < 0.1600:
                final_moving_direction = 'left'
                final_steps = '2'
            elif max(left_values) > max(right_values) and max(right_values) < 0.1600:
                final_moving_direction = 'right'
                final_steps = '2'
            else:
                final_moving_direction = 'Can\'t move, too many objects'
                final_steps = '0'
        elif len(directions) == 1:
            # In-case positions are 1 or 2 same output
            final_moving_direction = list(directions)[0]
            final_steps = max(moving_steps)
        elif len(positions) == 2 and len(directions) == 2:
            if 'center' not in positions:
                if max(moving_steps) > 0:
                    final_moving_direction = 'Can\'t move, too many objects'
                    final_steps = '0'
                else:
                    final_moving_direction = 'center'
                    final_steps = '0'
            elif 'right' not in positions:
                final_moving_direction = 'right'
                final_steps = max(moving_steps)
            else:
                final_moving_direction = 'left'
                final_steps = max(moving_steps)
        output_object = Output(final_moving_direction, final_steps, objects)
    return json.dumps(output_object, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class ObjectDetails:
    object_name = ''
    object_position = ''
    moving_direction = ''
    moving_steps = ''

    def __init__(self, name, position, direction, steps, left, right, center):
        self.object_name = name
        self.object_position = position
        self.moving_direction = direction
        self.moving_steps = steps
        self.left = left
        self.center = center
        self.right = right


class Output:
    objects = ''
    direction = ''
    steps = ''

    def __init__(self, direction, steps, objects):
        self.direction = direction
        self.steps = steps
        self.objects = objects


imageUrl = r"Testing Images/childBuggy.jpg"
with open(imageUrl, 'rb') as image_file:
    content = image_file.read()
image = vision.types.Image(content=content)
objects = detect_objects(image)
objects_detected = locate_object(objects)
output = final_directions(objects_detected)
print(output)

# Sample output
# [mid: "/m/04rmv"
# name: "Mouse"
# score: 0.8545877933502197
# bounding_poly {
#   normalized_vertices {
#     x: 0.030996425077319145
#     y: 0.12865036725997925
#   }
#   normalized_vertices {
#     x: 0.918846845626831
#     y: 0.12865036725997925
#   }
#   normalized_vertices {
#     x: 0.918846845626831
#     y: 0.7292723059654236
#   }
#   normalized_vertices {
#     x: 0.030996425077319145
#     y: 0.7292723059654236
#   }
# }
# , mid: "/m/0jbk"
# name: "Animal"
# score: 0.6630857586860657
# bounding_poly {
#   normalized_vertices {
#     x: 0.032450973987579346
#     y: 0.15275134146213531
#   }
#   normalized_vertices {
#     x: 0.8935753703117371
#     y: 0.15275134146213531
#   }
#   normalized_vertices {
#     x: 0.8935753703117371
#     y: 0.7078972458839417
#   }
#   normalized_vertices {
#     x: 0.032450973987579346
#     y: 0.7078972458839417
#   }
# }
# ]