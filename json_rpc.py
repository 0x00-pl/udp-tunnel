import json
import traceback

__author__ = 'pl'


def make_json_rpc_object():
    return {"jsonrpc": "2.0"}


def make_json_rpc_request(method, params, request_id=None):
    request = make_json_rpc_object()
    request['method'] = method
    request['params'] = params
    request['id'] = request_id
    return request


json_rpc_errors = {
    '-32700': {'code': -32700, 'message': 'Parse error'},  # Errors occurred on the server while parsing the JSON text.
    '-32600': {'code': -32600, 'message': 'Invalid Request'},  # The JSON sent is not a valid Request object.
    '-32601': {'code': -32601, 'message': 'Method not found'},  # The method does not exist / is not available.
    '-32602': {'code': -32602, 'message': 'Invalid params'},  # Invalid method parameter(s).
    '-32603': {'code': -32603, 'message': 'Internal error'},  # Internal JSON-RPC error.
    # -32000 to -32099 	Server error 	Reserved for implementation-defined server-errors.
}


def make_json_rpc_error(error_no, object_id=None):
    ret = make_json_rpc_object()
    ret['error'] = json_rpc_errors[str(error_no)]
    ret['id'] = object_id
    return ret


def make_json_rpc_result(result, object_id):
    ret = make_json_rpc_object()
    ret['result'] = result
    ret['id'] = object_id
    return ret


def call_json_rpc(request_json, methods, result_handler, args_extra):
    is_result = False
    try:
        rpc_object = json.loads(request_json.decode('utf-8'))
    except Exception as e:
        return make_json_rpc_error(-32700)

    try:
        assert (rpc_object['jsonrpc'] == '2.0')
        keys = rpc_object.keys()
        if 'error' in keys or 'result' in keys:
            is_result = True
        else:
            assert (type(rpc_object['method']) in (str,))
            rpc_object['params'] = rpc_object.get('params', None)
            rpc_object['id'] = rpc_object.get('id', None)
    except Exception as e:
        return make_json_rpc_error(-32600)

    if is_result is False:
        method = methods.get(rpc_object['method'], None)
        if method is None:
            return make_json_rpc_error(-32601, rpc_object['id'])

        try:
            result = method(rpc_object['params'], args_extra)
            object_id = rpc_object['id']
            if object_id is None:
                return None
        except Exception as e:
            traceback.print_exc()
            return make_json_rpc_error(-32603, rpc_object['id'])

        return make_json_rpc_result(result, object_id)
    else:
        if result_handler is not None:
            try:
                result_handler(rpc_object)
            except Exception as e:
                traceback.print_exc()
        return None
