"""Python wrappers around TensorFlow ops.

This file is MACHINE GENERATED! Do not edit.
Original C++ source file: gen_gcs_config_ops.cc
"""

import collections as _collections
import six as _six

from tensorflow.python import pywrap_tensorflow as _pywrap_tensorflow
from tensorflow.python.eager import context as _context
from tensorflow.python.eager import core as _core
from tensorflow.python.eager import execute as _execute
from tensorflow.python.framework import dtypes as _dtypes
from tensorflow.python.framework import errors as _errors
from tensorflow.python.framework import tensor_shape as _tensor_shape

from tensorflow.core.framework import op_def_pb2 as _op_def_pb2
# Needed to trigger the call to _set_call_cpp_shape_fn.
from tensorflow.python.framework import common_shapes as _common_shapes
from tensorflow.python.framework import op_def_registry as _op_def_registry
from tensorflow.python.framework import ops as _ops
from tensorflow.python.framework import op_def_library as _op_def_library
from tensorflow.python.util.tf_export import tf_export


@tf_export('gcs_configure_block_cache')
def gcs_configure_block_cache(max_cache_size, block_size, max_staleness, name=None):
  r"""TODO: add doc.

  Args:
    max_cache_size: A `Tensor` of type `uint64`.
    block_size: A `Tensor` of type `uint64`.
    max_staleness: A `Tensor` of type `uint64`.
    name: A name for the operation (optional).

  Returns:
    The created Operation.
  """
  _ctx = _context._context
  if _ctx is None or not _ctx._eager_context.is_eager:
    _, _, _op = _op_def_lib._apply_op_helper(
        "GcsConfigureBlockCache", max_cache_size=max_cache_size,
        block_size=block_size, max_staleness=max_staleness, name=name)
    return _op
    _result = None
    return _result

  else:
    try:
      _result = _pywrap_tensorflow.TFE_Py_FastPathExecute(
        _ctx._context_handle, _ctx._eager_context.device_name,
        "GcsConfigureBlockCache", name, _ctx._post_execution_callbacks,
        max_cache_size, block_size, max_staleness)
      return _result
    except _core._FallbackException:
      return gcs_configure_block_cache_eager_fallback(
          max_cache_size, block_size, max_staleness, name=name, ctx=_ctx)
    except _core._NotOkStatusException as e:
      if name is not None:
        message = e.message + " name: " + name
      else:
        message = e.message
      _six.raise_from(_core._status_to_exception(e.code, message), None)


def gcs_configure_block_cache_eager_fallback(max_cache_size, block_size, max_staleness, name=None, ctx=None):
  r"""This is the slowpath function for Eager mode.
  This is for function gcs_configure_block_cache
  """
  _ctx = ctx if ctx else _context.context()
  max_cache_size = _ops.convert_to_tensor(max_cache_size, _dtypes.uint64)
  block_size = _ops.convert_to_tensor(block_size, _dtypes.uint64)
  max_staleness = _ops.convert_to_tensor(max_staleness, _dtypes.uint64)
  _inputs_flat = [max_cache_size, block_size, max_staleness]
  _attrs = None
  _result = _execute.execute(b"GcsConfigureBlockCache", 0,
                             inputs=_inputs_flat, attrs=_attrs, ctx=_ctx,
                             name=name)
  _result = None
  return _result


@tf_export('gcs_configure_credentials')
def gcs_configure_credentials(json, name=None):
  r"""TODO: add doc.

  Args:
    json: A `Tensor` of type `string`.
    name: A name for the operation (optional).

  Returns:
    The created Operation.
  """
  _ctx = _context._context
  if _ctx is None or not _ctx._eager_context.is_eager:
    _, _, _op = _op_def_lib._apply_op_helper(
        "GcsConfigureCredentials", json=json, name=name)
    return _op
    _result = None
    return _result

  else:
    try:
      _result = _pywrap_tensorflow.TFE_Py_FastPathExecute(
        _ctx._context_handle, _ctx._eager_context.device_name,
        "GcsConfigureCredentials", name, _ctx._post_execution_callbacks, json)
      return _result
    except _core._FallbackException:
      return gcs_configure_credentials_eager_fallback(
          json, name=name, ctx=_ctx)
    except _core._NotOkStatusException as e:
      if name is not None:
        message = e.message + " name: " + name
      else:
        message = e.message
      _six.raise_from(_core._status_to_exception(e.code, message), None)


def gcs_configure_credentials_eager_fallback(json, name=None, ctx=None):
  r"""This is the slowpath function for Eager mode.
  This is for function gcs_configure_credentials
  """
  _ctx = ctx if ctx else _context.context()
  json = _ops.convert_to_tensor(json, _dtypes.string)
  _inputs_flat = [json]
  _attrs = None
  _result = _execute.execute(b"GcsConfigureCredentials", 0,
                             inputs=_inputs_flat, attrs=_attrs, ctx=_ctx,
                             name=name)
  _result = None
  return _result

def _InitOpDefLibrary(op_list_proto_bytes):
  op_list = _op_def_pb2.OpList()
  op_list.ParseFromString(op_list_proto_bytes)
  _op_def_registry.register_op_list(op_list)
  op_def_lib = _op_def_library.OpDefLibrary()
  op_def_lib.add_op_list(op_list)
  return op_def_lib
# op {
#   name: "GcsConfigureBlockCache"
#   input_arg {
#     name: "max_cache_size"
#     type: DT_UINT64
#   }
#   input_arg {
#     name: "block_size"
#     type: DT_UINT64
#   }
#   input_arg {
#     name: "max_staleness"
#     type: DT_UINT64
#   }
# }
# op {
#   name: "GcsConfigureCredentials"
#   input_arg {
#     name: "json"
#     type: DT_STRING
#   }
# }
_op_def_lib = _InitOpDefLibrary(b"\nO\n\026GcsConfigureBlockCache\022\022\n\016max_cache_size\030\027\022\016\n\nblock_size\030\027\022\021\n\rmax_staleness\030\027\n#\n\027GcsConfigureCredentials\022\010\n\004json\030\007")
