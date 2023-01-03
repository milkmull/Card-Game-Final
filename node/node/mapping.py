from .node_base import Port_Types

def find_all_input_ports(n, ports=None):
    if ports is None:
        ports = []
    
    if not n.is_flow:
        for ip in n.get_input_ports():
            if not ip.connection:
                ports.append(ip)
            else:
                find_all_input_ports(ip.connection, ports=ports)
                
    return ports

def find_all_nodes(_nodes):
    nodes = []
    group_nodes = []
    
    for n in _nodes:
        if n.is_group:
            group_nodes.append(n)
            data = find_all_nodes(n.nodes)
            nodes += data[0]
            group_nodes += data[1]
        else:
            nodes.append(n)
            
    return (list(set(nodes)), list(set(group_nodes)))

def find_visible_chunk(n, nodes, checked=None):
    if checked is None:
        checked = []
        
    if n.visible:
        nodes.append(n)
    checked.append(n)

    for ip in n.get_input_ports():
        if ip.connection:
            connected_node = ip.connection_port.parent
            if connected_node not in checked:
                find_visible_chunk(connected_node, nodes, checked=checked)
    
    for op in n.get_output_ports():
        if op.connection:
            connected_node = op.connection_port.parent
            if connected_node not in checked:
                find_visible_chunk(connected_node, nodes, checked=checked)
                
    return nodes
    
def find_chunk(n, nodes):
    nodes.append(n)
    
    for ip in n.get_input_ports():
        if ip.connection:
            connected_node = ip.connection_port.node
            if connected_node not in nodes:
                find_chunk(connected_node, nodes)
    
    for op in n.get_output_ports():
        if op.connection:
            connected_node = op.connection_port.node
            if connected_node not in nodes:
                find_chunk(connected_node, nodes)
                
    return nodes

def map_ports(n, ports, skip_ip=False, skip_op=False, all_ports=False, out_type=None, in_type=None): 
    if not skip_ip:
        for ip in n.get_input_ports():
            if not in_type or (in_type and ip.has_type(in_type)):
                if ip not in ports:
                    if ip.connection:
                        ports.append(ip)
                        op = ip.connection_port
                        if op not in ports:
                            map_ports(
                                op.node,
                                ports,
                                skip_ip=skip_ip,
                                skip_op=skip_op,
                                all_ports=all_ports,
                                out_type=out_type,
                                in_type=in_type
                            )
                    elif all_ports:
                        ports.append(ip)
            
    if not skip_op:
        for op in n.get_output_ports():
            if not out_type or (out_type and ip.has_type(out_type)):
                if op not in ports:
                    if op.connection:
                        ports.append(op)
                        ip = op.connection_port
                        if ip not in ports:
                            map_ports(
                                ip.node,
                                ports,
                                skip_ip=skip_ip,
                                skip_op=skip_op,
                                all_ports=all_ports,
                                out_type=out_type,
                                in_type=in_type
                            ) 
                    elif all_ports:
                        ports.append(op)
                
    return ports

def trace_flow(n, nodes, dir):
    nodes.append(n)
    
    if dir == -1:
        for ip in n.get_input_ports():
            if ip.connection:
                if ip.has_type(Port_Types.FLOW) and ip.connection not in nodes:
                    trace_flow(ip.connection, nodes, dir=dir)
                    
    elif dir == 1:
        for op in n.get_output_ports():
            if op.connection:
                if op.has_type(Port_Types.FLOW) and op.connection not in nodes:
                    trace_flow(op.connection, nodes, dir=dir)
                    
    return nodes

def find_parent_func(n):
    nodes = trace_flow(n, [], -1)
    for n in nodes:
        if n.is_func:
            return n

def find_lead(nodes):
    lead = nodes[0]
    for n in nodes:
        for op in n.get_output_ports():
            if op.is_flow:
                ips = n.get_input_ports()
                if not ips:
                    return n
                else:
                    for ip in ips:
                        if ip.is_flow and not ip.connection:
                            return n
            elif not n.get_input_ports():
                lead = n
                
    return lead
    
def map_flow(n, nodes, map, port=None, row=0, column=0):
    if column not in map:
        map[column] = {row: n}
    else:
        if row in map[column]:
            min_row = min({r for r in map[column]})
            max_row = max({r for r in map[column]})
            if abs(row - min_row) <= abs(row - max_row):
                row = min_row - 1
            else:
                row = max_row + 1
        map[column][row] = n
    nodes.remove(n)
    
    ipp = sorted([p for p in n.get_input_ports() if p.visible], key=lambda p: p.rect.top, reverse=True)
    i = ipp.index(port) if port in ipp else 0
    for j, ip in enumerate(ipp):
        if ip.connection:
            connected_node = ip.connection_port.parent
            if connected_node in nodes:
                map_flow(connected_node, nodes, map, port=ip.connection_port, row=row + (i - j), column=column - 1)

    opp = sorted([p for p in n.get_output_ports() if p.visible], key=lambda p: p.rect.top, reverse=True)
    i = opp.index(port) if port in opp else 0
    for j, op in enumerate(opp):
        if op.connection:# and not op.parent_port:
            connected_node = op.connection_port.parent
            if connected_node in nodes:
                map_flow(connected_node, nodes, map, port=op.connection_port, row=row + (i - j), column=column + 1)
            
    return map

def check_bad_connection(n0, n1):   
    local_funcs = set()
    scope_output = set()
    loop_output = set()
    
    nodes = find_chunk(n0, [])
    local_funcs = set([n for n in nodes if n.is_func])

    for n in nodes:
        out_port = None
        process_port = None
        check_ports = []
        for op in n.get_output_ports():
            if op.is_process:
                process_port = op
                if op.connection:
                    check_ports.append(op)
            elif op.has_type(Port_Types.FLOW):
                out_port = op
            elif op.connection:
                check_ports.append(op)
                
        if process_port and check_ports:
            for op in check_ports:
                ports = map_ports(op.connection, check_ports.copy(), all_ports=True, in_type=Port_Types.FLOW)
                if out_port in ports:
                    scope_output.add(op)

    opp = n0.get_output_ports()     
    for op in opp:
        if op.connection:
            ports = map_ports(op.connection, [], skip_ip=True)
            if any(op in ports for op in opp):
                loop_output.add(op)
            
    return (local_funcs, scope_output, loop_output)
