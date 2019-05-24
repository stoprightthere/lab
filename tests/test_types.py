# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import numpy as np
import pytest
import tensorflow as tf
import torch
from autograd import grad
from plum.promotion import _promotion_rule, convert

import lab as B
from .util import deq


def test_numeric():
    # Test convenient types.
    assert isinstance(1, B.Int)
    assert isinstance(np.int32(1), B.Int)
    assert isinstance(np.uint64(1), B.Int)
    assert isinstance(1.0, B.Float)
    assert isinstance(np.float32(1), B.Float)
    assert isinstance(True, B.Bool)
    assert isinstance(np.bool_(True), B.Bool)
    assert isinstance(np.uint(1), B.Number)
    assert isinstance(np.float64(1), B.Number)

    # Test NumPy.
    assert isinstance(1, B.NPNumeric)
    assert isinstance(np.bool_(1), B.NPNumeric)
    assert isinstance(np.float32(1), B.NPNumeric)
    assert isinstance(np.array(1), B.NPNumeric)

    # Test TensorFlow.
    assert isinstance(tf.constant(1), B.TFNumeric)
    assert isinstance(tf.Variable(1), B.TFNumeric)

    # Test Torch.
    assert isinstance(torch.tensor(1), B.TorchNumeric)

    # Test general numeric type.
    assert isinstance(1, B.Numeric)
    assert isinstance(np.bool_(1), B.Numeric)
    assert isinstance(np.float64(1), B.Numeric)
    assert isinstance(np.array(1), B.Numeric)
    assert isinstance(tf.constant(1), B.Numeric)
    assert isinstance(torch.tensor(1), B.Numeric)

    # Test promotion.
    assert _promotion_rule(np.array(1), tf.constant(1)) == B.TFNumeric
    assert _promotion_rule(np.array(1), tf.Variable(1)) == B.TFNumeric
    assert _promotion_rule(tf.constant(1), tf.Variable(1)) == B.TFNumeric
    assert _promotion_rule(np.array(1), torch.tensor(1)) == B.TorchNumeric
    with pytest.raises(TypeError):
        _promotion_rule(B.TFNumeric, B.TorchNumeric)

    # Test conversion.
    assert isinstance(convert(np.array(1), B.TFNumeric), B.TFNumeric)
    assert isinstance(convert(np.array(1), B.TorchNumeric), B.TorchNumeric)


def test_autograd_tracing():
    found_objs = []

    def f(x):
        found_objs.append(x)
        return B.sum(x)

    # Test that function runs.
    f(np.ones(5))
    grad(f)(np.ones(5))

    # Test that objects are of the right type.
    for obj in found_objs:
        assert isinstance(obj, B.NPNumeric)


def test_dimension():
    for t in [B.NPDimension, B.TFDimension, B.TorchDimension, B.Dimension]:
        assert isinstance(1, t)
    assert isinstance(tf.ones((1, 1)).shape[0], B.Dimension)


def test_data_type():
    assert isinstance(np.float32, B.NPDType)
    assert isinstance(np.float32, B.DType)
    assert isinstance(tf.float32, B.TFDType)
    assert isinstance(tf.float32, B.DType)
    assert isinstance(torch.float32, B.TorchDType)
    assert isinstance(torch.float32, B.DType)

    # Test conversion between data types.
    deq(convert(np.float32, B.TFDType), tf.float32)
    deq(convert(np.float32, B.TorchDType), torch.float32)
    deq(convert(tf.float32, B.NPDType), np.float32)
    deq(convert(tf.float32, B.TorchDType), torch.float32)
    deq(convert(torch.float32, B.NPDType), np.float32)
    deq(convert(torch.float32, B.TFDType), tf.float32)

    # Test conversion of `np.dtype`.
    deq(convert(np.dtype('float32'), B.DType), np.float32)


def test_issubdtype():
    assert B.issubdtype(np.float32, np.floating)
    assert B.issubdtype(tf.float32, np.floating)
    assert B.issubdtype(torch.float32, np.floating)
    assert not B.issubdtype(np.float32, np.integer)
    assert not B.issubdtype(tf.float32, np.integer)
    assert not B.issubdtype(torch.float32, np.integer)


def test_dtype():
    assert B.dtype(1) == int
    assert B.dtype(1.0) == float
    assert B.dtype(np.array(1, dtype=np.int32)) == np.int32
    assert B.dtype(np.array(1.0, dtype=np.float32)) == np.float32
    assert B.dtype(tf.constant(1, dtype=tf.int32)) == tf.int32
    assert B.dtype(tf.constant(1.0, dtype=tf.float32)) == tf.float32
    assert B.dtype(torch.tensor(1, dtype=torch.int32)) == torch.int32
    assert B.dtype(torch.tensor(1.0, dtype=torch.float32)) == torch.float32


def test_framework():
    for t in [B.NP, B.Framework]:
        assert isinstance(np.array(1), t)
        assert isinstance(1, t)
        assert isinstance(np.float32, t)

    for t in [B.TF, B.Framework]:
        assert isinstance(tf.constant(1), t)
        assert isinstance(1, t)
        assert isinstance(tf.ones((1, 1)).shape[0], t)
        assert isinstance(tf.float32, t)

    for t in [B.Torch, B.Framework]:
        assert isinstance(torch.tensor(1), t)
        assert isinstance(1, t)
        assert isinstance(torch.float32, t)
