from collections import namedtuple

import parse

Function = namedtuple('Function', ['name', 'arguments', 'return_types', 'namespace', 'body'])
Variable = namedtuple('Variable', ['name', 'type'])

Create_variable = namedtuple('Create_variable', ['name', 'type'])
Set_variable = namedtuple('Set_variable', ['name', 'type', 'value'])

Add = namedtuple('Add', ['first', 'second', 'target'])

Temporary = namedtuple('Temporary', 'index')

def gen_ir(parsed):
	def temporary():
		nonlocal temporary_index

		index = temporary_index

		temporary_index += 1

		return Temporary(index)

	def expression(parsed, result_variable_name, result_variable_type):
		ir = []

		if type(parsed) == parse.Integer_literal:
			ir.append(Set_variable(result_variable_name, result_variable_type, parsed.value))

		# TODO: don't hardcode the name, use an object instead
		if type(parsed) == parse.Function_call:
			if parsed.name == ['+']: 
				assert len(parsed.arguments) == 2

				first = temporary()
				second = temporary()

				ir.append(Create_variable(first, result_variable_type))
				ir.append(Create_variable(second, result_variable_type))

				ir.extend(expression(parsed.arguments[0], first, result_variable_type))
				ir.extend(expression(parsed.arguments[1], first, result_variable_type))

				ir.append(Add(first, second, result_variable_name))

			else:
				# FIXME: throw error
				print('Function call not implemented: %s' % parsed)
			

		else:
			# FIXME: throw error
			print('Unknown node type %s' % type(parsed))

		return ir
		
	def block(parsed, namespaces = ()):
		own_namespace = []
		ir = []

		for node in parsed:
			if type(node) == parse.Function_definition:
				body, inner_namespace = block(node.body, namespaces + (own_namespace,))

				own_namespace.append(Function(node.name, node.arguments, node.return_types, inner_namespace, body))

				# TODO: Represent functions with a real type
				ir.append(Create_variable(node.name, None))

			elif type(node) == parse.Let_statement:
				ir.append(Create_variable(node.name, node.type))
				ir.extend(expression(node.initializer, node.name, node.type))

				own_namespace.append

			else:
				# FIXME: throw error
				print('Unknown node type %s' % type(node))

		return ir, own_namespace

	temporary_index = 0

	return block(parsed)

def prettyprint_ir(bundle):
	ir, namespace = bundle
	for element in ir:
		print(element)

	print()

	for function in namespace:
		print('function: name: %s args: %s return: %s' % (function.name, function.arguments, function.return_types))
		for element in function.body:
			print('\t' + str(element))
