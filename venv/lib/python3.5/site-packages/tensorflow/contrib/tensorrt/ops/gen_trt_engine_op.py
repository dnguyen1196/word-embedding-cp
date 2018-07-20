"""Python wrappers around TensorFlow ops.

This file is MACHINE GENERATED! Do not edit.
Original C++ source file: trt_engine_op.cc
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


@tf_export('trt_calib_op')
def trt_calib_op(in_tensor, segment_nodes, segment_output_names, input_names, resource_name, name=None):
  r"""TODO: add doc.

  Args:
    in_tensor: A list of `Tensor` objects with types from: `int8`, `half`, `float32`.
    segment_nodes: A list of `strings`.
    segment_output_names: A list of `strings`.
    input_names: A list of `strings`.
    resource_name: A `string`.
    name: A name for the operation (optional).

  Returns:
    A list of `Tensor` objects. Has the same type as `in_tensor`.
  """
  _ctx = _context._context
  if _ctx is None or not _ctx._eager_context.is_eager:
    if not isinstance(segment_nodes, (list, tuple)):
      raise TypeError(
          "Expected list for 'segment_nodes' argument to "
          "'trt_calib_op' Op, not %r." % segment_nodes)
    segment_nodes = [_execute.make_str(_s, "segment_nodes") for _s in segment_nodes]
    if not isinstance(segment_output_names, (list, tuple)):
      raise TypeError(
          "Expected list for 'segment_output_names' argument to "
          "'trt_calib_op' Op, not %r." % segment_output_names)
    segment_output_names = [_execute.make_str(_s, "segment_output_names") for _s in segment_output_names]
    if not isinstance(input_names, (list, tuple)):
      raise TypeError(
          "Expected list for 'input_names' argument to "
          "'trt_calib_op' Op, not %r." % input_names)
    input_names = [_execute.make_str(_s, "input_names") for _s in input_names]
    resource_name = _execute.make_str(resource_name, "resource_name")
    _, _, _op = _op_def_lib._apply_op_helper(
        "TRTCalibOp", in_tensor=in_tensor, segment_nodes=segment_nodes,
        segment_output_names=segment_output_names, input_names=input_names,
        resource_name=resource_name, name=name)
    _result = _op.outputs[:]
    _inputs_flat = _op.inputs
    _attrs = ("segment_nodes", _op.get_attr("segment_nodes"),
              "segment_output_names", _op.get_attr("segment_output_names"),
              "input_names", _op.get_attr("input_names"), "resource_name",
              _op.get_attr("resource_name"), "InT", _op.get_attr("InT"))
    _execute.record_gradient(
      "TRTCalibOp", _inputs_flat, _attrs, _result, name)
    return _result

  else:
    try:
      _result = _pywrap_tensorflow.TFE_Py_FastPathExecute(
        _ctx._context_handle, _ctx._eager_context.device_name, "TRTCalibOp",
        name, _ctx._post_execution_callbacks, in_tensor, "segment_nodes",
        segment_nodes, "segment_output_names", segment_output_names,
        "input_names", input_names, "resource_name", resource_name)
      return _result
    except _core._FallbackException:
      return trt_calib_op_eager_fallback(
          in_tensor, segment_nodes=segment_nodes,
          segment_output_names=segment_output_names, input_names=input_names,
          resource_name=resource_name, name=name, ctx=_ctx)
    except _core._NotOkStatusException as e:
      if name is not None:
        message = e.message + " name: " + name
      else:
        message = e.message
      _six.raise_from(_core._status_to_exception(e.code, message), None)


def trt_calib_op_eager_fallback(in_tensor, segment_nodes, segment_output_names, input_names, resource_name, name=None, ctx=None):
  r"""This is the slowpath function for Eager mode.
  This is for function trt_calib_op
  """
  _ctx = ctx if ctx else _context.context()
  if not isinstance(segment_nodes, (list, tuple)):
    raise TypeError(
        "Expected list for 'segment_nodes' argument to "
        "'trt_calib_op' Op, not %r." % segment_nodes)
  segment_nodes = [_execute.make_str(_s, "segment_nodes") for _s in segment_nodes]
  if not isinstance(segment_output_names, (list, tuple)):
    raise TypeError(
        "Expected list for 'segment_output_names' argument to "
        "'trt_calib_op' Op, not %r." % segment_output_names)
  segment_output_names = [_execute.make_str(_s, "segment_output_names") for _s in segment_output_names]
  if not isinstance(input_names, (list, tuple)):
    raise TypeError(
        "Expected list for 'input_names' argument to "
        "'trt_calib_op' Op, not %r." % input_names)
  input_names = [_execute.make_str(_s, "input_names") for _s in input_names]
  resource_name = _execute.make_str(resource_name, "resource_name")
  _attr_InT, in_tensor = _execute.convert_to_mixed_eager_tensors(in_tensor, _ctx)
  _inputs_flat = list(in_tensor)
  _attrs = ("segment_nodes", segment_nodes, "segment_output_names",
  segment_output_names, "input_names", input_names, "resource_name",
  resource_name, "InT", _attr_InT)
  _result = _execute.execute(b"TRTCalibOp", len(in_tensor),
                             inputs=_inputs_flat, attrs=_attrs, ctx=_ctx,
                             name=name)
  _execute.record_gradient(
      "TRTCalibOp", _inputs_flat, _attrs, _result, name)
  return _result

_ops.RegisterShape("TRTCalibOp")(None)


@tf_export('trt_engine_op')
def trt_engine_op(in_tensor, serialized_engine, input_nodes, output_nodes, OutT, name=None):
  r"""TODO: add doc.

  Args:
    in_tensor: A list of `Tensor` objects with types from: `float32`.
    serialized_engine: A `string`.
    input_nodes: A list of `strings`.
    output_nodes: A list of `strings`.
    OutT: A list of `tf.DTypes` from: `tf.float32` that has length `>= 1`.
    name: A name for the operation (optional).

  Returns:
    A list of `Tensor` objects of type `OutT`.
  """
  _ctx = _context._context
  if _ctx is None or not _ctx._eager_context.is_eager:
    serialized_engine = _execute.make_str(serialized_engine, "serialized_engine")
    if not isinstance(input_nodes, (list, tuple)):
      raise TypeError(
          "Expected list for 'input_nodes' argument to "
          "'trt_engine_op' Op, not %r." % input_nodes)
    input_nodes = [_execute.make_str(_s, "input_nodes") for _s in input_nodes]
    if not isinstance(output_nodes, (list, tuple)):
      raise TypeError(
          "Expected list for 'output_nodes' argument to "
          "'trt_engine_op' Op, not %r." % output_nodes)
    output_nodes = [_execute.make_str(_s, "output_nodes") for _s in output_nodes]
    if not isinstance(OutT, (list, tuple)):
      raise TypeError(
          "Expected list for 'OutT' argument to "
          "'trt_engine_op' Op, not %r." % OutT)
    OutT = [_execute.make_type(_t, "OutT") for _t in OutT]
    _, _, _op = _op_def_lib._apply_op_helper(
        "TRTEngineOp", in_tensor=in_tensor,
        serialized_engine=serialized_engine, input_nodes=input_nodes,
        output_nodes=output_nodes, OutT=OutT, name=name)
    _result = _op.outputs[:]
    _inputs_flat = _op.inputs
    _attrs = ("serialized_engine", _op.get_attr("serialized_engine"),
              "input_nodes", _op.get_attr("input_nodes"), "output_nodes",
              _op.get_attr("output_nodes"), "InT", _op.get_attr("InT"),
              "OutT", _op.get_attr("OutT"))
    _execute.record_gradient(
      "TRTEngineOp", _inputs_flat, _attrs, _result, name)
    return _result

  else:
    try:
      _result = _pywrap_tensorflow.TFE_Py_FastPathExecute(
        _ctx._context_handle, _ctx._eager_context.device_name, "TRTEngineOp",
        name, _ctx._post_execution_callbacks, in_tensor, "serialized_engine",
        serialized_engine, "input_nodes", input_nodes, "output_nodes",
        output_nodes, "OutT", OutT)
      return _result
    except _core._FallbackException:
      return trt_engine_op_eager_fallback(
          in_tensor, serialized_engine=serialized_engine,
          input_nodes=input_nodes, output_nodes=output_nodes, OutT=OutT,
          name=name, ctx=_ctx)
    except _core._NotOkStatusException as e:
      if name is not None:
        message = e.message + " name: " + name
      else:
        message = e.message
      _six.raise_from(_core._status_to_exception(e.code, message), None)


def trt_engine_op_eager_fallback(in_tensor, serialized_engine, input_nodes, output_nodes, OutT, name=None, ctx=None):
  r"""This is the slowpath function for Eager mode.
  This is for function trt_engine_op
  """
  _ctx = ctx if ctx else _context.context()
  serialized_engine = _execute.make_str(serialized_engine, "serialized_engine")
  if not isinstance(input_nodes, (list, tuple)):
    raise TypeError(
        "Expected list for 'input_nodes' argument to "
        "'trt_engine_op' Op, not %r." % input_nodes)
  input_nodes = [_execute.make_str(_s, "input_nodes") for _s in input_nodes]
  if not isinstance(output_nodes, (list, tuple)):
    raise TypeError(
        "Expected list for 'output_nodes' argument to "
        "'trt_engine_op' Op, not %r." % output_nodes)
  output_nodes = [_execute.make_str(_s, "output_nodes") for _s in output_nodes]
  if not isinstance(OutT, (list, tuple)):
    raise TypeError(
        "Expected list for 'OutT' argument to "
        "'trt_engine_op' Op, not %r." % OutT)
  OutT = [_execute.make_type(_t, "OutT") for _t in OutT]
  _attr_InT, in_tensor = _execute.convert_to_mixed_eager_tensors(in_tensor, _ctx)
  _inputs_flat = list(in_tensor)
  _attrs = ("serialized_engine", serialized_engine, "input_nodes",
  input_nodes, "output_nodes", output_nodes, "InT", _attr_InT, "OutT", OutT)
  _result = _execute.execute(b"TRTEngineOp", len(OutT), inputs=_inputs_flat,
                             attrs=_attrs, ctx=_ctx, name=name)
  _execute.record_gradient(
      "TRTEngineOp", _inputs_flat, _attrs, _result, name)
  return _result

_ops.RegisterShape("TRTEngineOp")(None)

def _InitOpDefLibrary(op_list_proto_bytes):
  op_list = _op_def_pb2.OpList()
  op_list.ParseFromString(op_list_proto_bytes)
  _op_def_registry.register_op_list(op_list)
  op_def_lib = _op_def_library.OpDefLibrary()
  op_def_lib.add_op_list(op_list)
  return op_def_lib
# op {
#   name: "TRTCalibOp"
#   input_arg {
#     name: "in_tensor"
#     type_list_attr: "InT"
#   }
#   output_arg {
#     name: "out_tensor"
#     type_list_attr: "InT"
#   }
#   attr {
#     name: "segment_nodes"
#     type: "list(string)"
#   }
#   attr {
#     name: "segment_output_names"
#     type: "list(string)"
#   }
#   attr {
#     name: "input_names"
#     type: "list(string)"
#   }
#   attr {
#     name: "resource_name"
#     type: "string"
#   }
#   attr {
#     name: "InT"
#     type: "list(type)"
#     has_minimum: true
#     minimum: 1
#     allowed_values {
#       list {
#         type: DT_INT8
#         type: DT_HALF
#         type: DT_FLOAT
#       }
#     }
#   }
# }
# op {
#   name: "TRTEngineOp"
#   input_arg {
#     name: "in_tensor"
#     type_list_attr: "InT"
#   }
#   output_arg {
#     name: "out_tensor"
#     type_list_attr: "OutT"
#   }
#   attr {
#     name: "serialized_engine"
#     type: "string"
#   }
#   attr {
#     name: "input_nodes"
#     type: "list(string)"
#   }
#   attr {
#     name: "output_nodes"
#     type: "list(string)"
#   }
#   attr {
#     name: "InT"
#     type: "list(type)"
#     has_minimum: true
#     minimum: 1
#     allowed_values {
#       list {
#         type: DT_FLOAT
#       }
#     }
#   }
#   attr {
#     name: "OutT"
#     type: "list(type)"
#     has_minimum: true
#     minimum: 1
#     allowed_values {
#       list {
#         type: DT_FLOAT
#       }
#     }
#   }
# }
_op_def_lib = _InitOpDefLibrary(b"\n\314\001\n\nTRTCalibOp\022\020\n\tin_tensor2\003InT\032\021\n\nout_tensor2\003InT\"\035\n\rsegment_nodes\022\014list(string)\"$\n\024segment_output_names\022\014list(string)\"\033\n\013input_names\022\014list(string)\"\027\n\rresource_name\022\006string\"\036\n\003InT\022\nlist(type)(\0010\001:\007\n\0052\003\006\023\001\n\310\001\n\013TRTEngineOp\022\020\n\tin_tensor2\003InT\032\022\n\nout_tensor2\004OutT\"\033\n\021serialized_engine\022\006string\"\033\n\013input_nodes\022\014list(string)\"\034\n\014output_nodes\022\014list(string)\"\034\n\003InT\022\nlist(type)(\0010\001:\005\n\0032\001\001\"\035\n\004OutT\022\nlist(type)(\0010\001:\005\n\0032\001\001")
