import os
import io
from google.cloud import vision
from google.cloud.vision import types

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'level-choir-270012-9c065919be6c.json'


def detect_objects(image):
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    objects = client.object_localization(image=image).localized_object_annotations
    # print('Object ', objects)
    # print('Number of objects found: {}'.format(len(objects)))
    # for object_ in objects:
    #     print('\n{} (confidence: {})'.format(object_.name, object_.score))
    #     print('Normalized bounding polygon vertices: ')
    #     for vertex in object_.bounding_poly.normalized_vertices:
    #         print(' - ({}, {})'.format(vertex.x, vertex.y))

    return objects


imageUrl = r"BritishShorthair_body_6.jpg"
with open(imageUrl, 'rb') as image_file:
    content = image_file.read()
image = vision.types.Image(content=content)


def locate_object(objects):

    x_vertices = set()
    y_vertices = set()
    for object in objects:
        left = 0.0
        center = 0.0
        right = 0.0
        if object.score > 0.25:
            for vertex in object.bounding_poly.normalized_vertices:
                x_vertices.add(round(vertex.x, 4))
                y_vertices.add(round(vertex.y, 4))
            x_vertices = sorted(x_vertices)
            y_vertices = sorted(y_vertices)
            object_width = x_vertices[1] - x_vertices[0]
            object_height = y_vertices[1] - y_vertices[0]

            if x_vertices[0] < 0.3333:
                if x_vertices[1] < 0.3333:
                    left = object_width
                elif x_vertices[1] < 0.6666:
                    left = 0.3333 - x_vertices[0]
                    center = x_vertices[1] - 0.3333
                elif x_vertices[1] <= 1:
                    left = 0.3333 - x_vertices[0]
                    center = 0.3333
                    right = x_vertices[1] - 0.6666

            if 0.6666 > x_vertices[0] > 0.3333:
                if x_vertices[1] < 0.6666:
                    center = object_width
                elif x_vertices[1] <= 1:
                    center = 0.3333 - x_vertices[0]
                    right = x_vertices[1] - 0.6666

            if x_vertices[0] > 0.6666:
                right = object_width

            print(left)
            print(center)
            print(right)


objects = detect_objects(image)
locate_object(objects)


def max_value(value, threshold):
    if value > threshold:
        return threshold
    else:
        return value


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