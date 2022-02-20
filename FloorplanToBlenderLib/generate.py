from . import IO
from . import const
from . import config
import numpy as np

from FloorplanToBlenderLib.generator import Door, Floor, Room, Wall, Window

"""
Generate
This file contains code for generate data files, used when creating blender project.
A temp storage of calculated data and a way to transfer data to the blender script.

FloorplanToBlender3d
Copyright (C) 2021 Daniel Westberg
"""

def generate_all_files(floorplan, info, world_direction = None, world_position = np.array([0,0,0]), world_rotation = np.array([0,0,0])):
    """
    Generate all data files
    @Param image path
    @Param dir build in negative or positive direction
    @Param info, boolean if should be printed
    @Param position, vector of float
    @Param rotation, vector of float
    @Return path to generated file, shape
    """

    if world_direction is None:
        world_direction = 1

    if info:
        print(
            " ----- Generate ",
            floorplan.image_path,
            " at pos ",
            floorplan.position+world_position,
            " rot ",
            floorplan.rotation+world_rotation,
            " -----",
        )

    # Get path to save data
    path = IO.create_new_floorplan_path(const.BASE_PATH)

    origin_path, shape = IO.find_reuseable_data(floorplan.image_path, const.BASE_PATH)

    if origin_path is None: 
        origin_path = path

        _, gray, scale_factor = IO.read_image(floorplan.image_path, floorplan)


        if floorplan.floors:
            shape = Floor(gray, path, info).shape

        if floorplan.walls:
            new_shape = Wall(gray, path, info).shape
            shape = validate_shape(shape, new_shape)

        if floorplan.rooms:
            new_shape = Room(gray, path, info).shape
            shape = validate_shape(shape, new_shape)

        if floorplan.windows:
            Window(gray, path, floorplan.image_path, scale_factor, info)

        if floorplan.doors:
            Door(gray, path, floorplan.image_path, scale_factor, info)

    generate_transform_file(
        floorplan.image_path, path, info, floorplan.position, world_position, floorplan.rotation, world_rotation, shape, path, origin_path
    )

    if floorplan.position is not None:
        shape = [world_direction*shape[0] + floorplan.position[0], world_direction*shape[1] + floorplan.position[1], world_direction*shape[2] + floorplan.position[2]]

    return path, shape


def validate_shape(old_shape, new_shape):
    """
    Validate shape, use this to calculate a objects total shape
    @Param old_shape
    @Param new_shape
    @Return total shape
    """
    shape = [0, 0, 0]
    shape[0] = max(old_shape[0], new_shape[0])
    shape[1] = max(old_shape[1], new_shape[1])
    shape[2] = max(old_shape[2], new_shape[2])
    return shape


def generate_transform_file(
    img_path, path, info, position, world_position, rotation, world_rotation, shape, data_path, origin_path
):  # TODO: add scaling
    """
    Generate transform of file
    A transform contains information about an objects position, rotation.
    @Param img_path
    @Param info, boolean if should be printed
    @Param position, position vector
    @Param rotation, rotation vector
    @Param shape
    @Return transform
    """
    # create map
    transform = {}
    if position is None:
        transform[const.STR_POSITION] = (0, 0, 0)
    else:
        transform[const.STR_POSITION] = position

    if rotation is None:
        transform[const.STR_ROTATION] = (0, 0, 0)
    else:
        transform[const.STR_ROTATION] = rotation

    if world_position is None:
        transform["world_position"] = (0, 0, 0)
    else:
        transform["world_position"] = world_position

    if world_rotation is None:
        transform["world_rotation"] = (0, 0, 0)
    else:
        transform["world_rotation"] = world_rotation

    if shape is None:
        transform[const.STR_SHAPE] = (0, 0, 0)
    else:
        transform[const.STR_SHAPE] = shape

    transform[const.STR_IMAGE_PATH] = img_path

    transform[const.STR_ORIGIN_PATH] = origin_path

    transform[const.STR_DATA_PATH] = data_path

    IO.save_to_file(path + "transform", transform, info)

    return transform
