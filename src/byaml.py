import enum
import io
import mathutils
from . import binary_io

class ByamlFile:
    class Header:
        def __init__(self, reader):
            if reader.read_raw_string(2) != "BY":
                raise AssertionError("Invalid BYAML header.")
            if reader.read_uint16() != 0x0001:
                raise AssertionError("Unsupported BYAML version.")
            self.name_array_node_offset = reader.read_uint32()
            self.string_array_node_offset = reader.read_uint32()
            self.path_array_node_offset = reader.read_uint32()
            self.root_node_offset = reader.read_uint32()

    def __init__(self, raw):
        # Open a big-endian binary reader on the stream.
        with binary_io.BinaryReader(raw) as reader:
            reader.endianness = ">"
            header = self.Header(reader)
            # Read the name array node, holding string referenced by index for the name of other nodes.
            reader.seek(header.name_array_node_offset)
            self.name_array_node = ByamlNode.from_file(self, reader)
            # Read the string array node, holding strings referenced by index in string nodes.
            reader.seek(header.string_array_node_offset)
            self.string_array_node = ByamlNode.from_file(self, reader)
            # Read the optional path array node, holding paths referenced by index in path nodes.
            if header.path_array_node_offset:
                reader.seek(header.path_array_node_offset)
                self.path_array_node = ByamlNode.from_file(self, reader)
            # Read the root node.
            reader.seek(header.root_node_offset)
            self.root = ByamlNode.from_file(self, reader)

class ByamlNodeType(enum.IntEnum):
    StringIndex = 0xA0,  # 160
    PathIndex   = 0xA1,  # 161
    Array       = 0xC0,  # 192
    Dictionary  = 0xC1,  # 193
    StringArray = 0xC2,  # 194
    PathArray   = 0xC3,  # 195
    Boolean     = 0xD0,  # 208
    Integer     = 0xD1,  # 209
    Float       = 0xD2   # 210

class ByamlNode:
    @staticmethod
    def from_file(byaml_file, reader, node_type=None):
        # Read the node type if it has not been provided yet.
        node_type_given = bool(node_type)
        if not node_type_given:
            node_type = reader.read_byte()
        if ByamlNodeType.Array <= node_type <= ByamlNodeType.PathArray:
            # Get the length of array nodes.
            old_pos = None
            if node_type_given:
                # If the node type was given, the array node is read from an offset.
                offset = reader.read_uint32()
                old_pos = reader.tell()
                reader.seek(offset)
            else:
                reader.seek(-1, io.SEEK_CUR)
            length = reader.read_uint32() & 0x00FFFFFF
            if   node_type == ByamlNodeType.Array:       node = ByamlArrayNode.from_file(byaml_file, reader, length)
            elif node_type == ByamlNodeType.Dictionary:  node = ByamlDictionaryNode.from_file(byaml_file, reader, length)
            elif node_type == ByamlNodeType.StringArray: node = ByamlStringArrayNode.from_file(byaml_file, reader, length)
            elif node_type == ByamlNodeType.PathArray:   node = ByamlPathArrayNode.from_file(byaml_file, reader, length)
            else: raise AssertionError("Unknown node type " + str(node_type) + ".")
            # Seek back to the previous position if this was a node positioned at an offset.
            if old_pos:
                reader.seek(old_pos)
            return node
        else:
            # Value nodes parse the following uint32 themselves.
            if   node_type == ByamlNodeType.StringIndex: return ByamlStringNode.from_file(byaml_file, reader)
            elif node_type == ByamlNodeType.PathIndex:   return ByamlPathNode.from_file(byaml_file, reader)
            elif node_type == ByamlNodeType.Boolean:     return ByamlBooleanNode.from_file(byaml_file, reader)
            elif node_type == ByamlNodeType.Integer:     return ByamlIntegerNode.from_file(byaml_file, reader)
            elif node_type == ByamlNodeType.Float:       return ByamlFloatNode.from_file(byaml_file, reader)
            else: raise AssertionError("Unknown node type " + str(node_type) + ".")

# ---- Element Nodes ---------------------------------------------------------------------------------------------------

class ByamlElementNode(ByamlNode):
    def __init__(self):
        self.value = None

    def __delitem__(self, key):
        del self.value[key]

    def __getitem__(self, item):
        return self.value[item]

    def __setitem__(self, key, value):
        self.value[key] = value

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return iter(self.value)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.value)

    def get(self, key, default=None):
        return self.value.get(key, default)

    def get_value(self, key, default=None):
        element = self.value.get(key)
        return element.value if element else default

class ByamlArrayNode(ByamlElementNode):
    @staticmethod
    def from_file(byaml_file, reader, length):
        self = ByamlArrayNode()
        # Read the element types of the array.
        node_types = reader.read_bytes(length)
        # Read the elements, which begin after a padding to the next 4 bytes.
        reader.seek(-reader.tell() % 4, io.SEEK_CUR)
        self.value = []
        for i in range(0, length):
            self.value.append(ByamlNode.from_file(byaml_file, reader, node_types[i]))
        return self

class ByamlDictionaryNode(ByamlElementNode):
    @staticmethod
    def from_file(byaml_file, reader, length):
        self = ByamlDictionaryNode()
        # Read the elements of the dictionary.
        self.value = {}
        for i in range(0, length):
            value = reader.read_uint32()
            node_name_index = value >> 8 & 0xFFFFFFFF
            node_type = value & 0x000000FF
            node_name = byaml_file.name_array_node[node_name_index]
            self.value[node_name] = ByamlNode.from_file(byaml_file, reader, node_type)
        return self

    def to_vector(self):
        return mathutils.Vector((self.value["X"].value, -self.value["Z"].value, self.value["Y"].value))

class ByamlStringArrayNode(ByamlElementNode):
    @staticmethod
    def from_file(byaml_file, reader, length):
        self = ByamlStringArrayNode()
        node_offset = reader.tell() - 4  # String offsets are relative to the start of this node.
        # Read the element offsets.
        offsets = reader.read_uint32s(length)
        # Read the strings by seeking to their element offset and then back.
        self.value = []
        old_position = reader.tell()
        for i in range(0, length):
            reader.seek(node_offset + offsets[i])
            self.value.append(reader.read_0_string())
        reader.seek(old_position)
        return self

class ByamlPathArrayNode(ByamlElementNode):
    @staticmethod
    def from_file(byaml_file, reader, length):
        self = ByamlStringArrayNode()
        node_offset = reader.tell() - 4  # String offsets are relative to the start of this node.
        # Read the element offsets.
        offsets = reader.read_uint32s(length + 1)
        # Read the strings by seeking to their element offset and then back.
        self.value = []
        old_position = reader.tell()
        for i in range(0, length):
            reader.seek(node_offset + offsets[i])
            point_count = (offsets[i + 1] - offsets[i]) // 0x1C
            self.value.append(ByamlPath.from_file(reader, point_count))
        reader.seek(old_position)
        return self

# ---- Index Nodes -----------------------------------------------------------------------------------------------------

class ByamlIndexNode(ByamlNode):
    def __init__(self):
        self.index = None
        self.value = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.value

class ByamlStringNode(ByamlIndexNode):
    @staticmethod
    def from_file(byaml_file, reader):
        self = ByamlStringNode()
        self.index = reader.read_uint32()
        self.value = byaml_file.string_array_node[self.index]
        return self

class ByamlPathNode(ByamlIndexNode):
    @staticmethod
    def from_file(byaml_file, reader):
        self = ByamlPathNode()
        self.index = reader.read_uint32()
        self.value = byaml_file.path_array_node[self.index]
        return self

# ---- Value Nodes -----------------------------------------------------------------------------------------------------

class ByamlValueNode(ByamlNode):
    def __init__(self):
        self.value = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.value)

class ByamlBooleanNode(ByamlValueNode):
    @staticmethod
    def from_file(byaml_file, reader):
        self = ByamlBooleanNode()
        self.value = reader.read_uint32() != 0
        return self

class ByamlIntegerNode(ByamlValueNode):
    @staticmethod
    def from_file(byaml_file, reader):
        self = ByamlIntegerNode()
        self.value = reader.read_int32()
        return self

class ByamlFloatNode(ByamlValueNode):
    @staticmethod
    def from_file(byaml_file, reader):
        self = ByamlFloatNode()
        self.value = reader.read_single()
        return self

# ---- Path ------------------------------------------------------------------------------------------------------------

class ByamlPath:
    @staticmethod
    def from_file(reader, point_count):
        self = ByamlPath()
        self.points = []
        for i in range(0, point_count):
            self.points.append(ByamlPathPoint.from_file(reader))
        return self

    def __init__(self):
        self.points = None

    def __delitem__(self, key):
        del self.points[key]

    def __getitem__(self, item):
        return self.points[item]

    def __setitem__(self, key, value):
        self.points[key] = value

    def __len__(self):
        return len(self.points)

    def __iter__(self):
        return iter(self.points)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.points)

class ByamlPathPoint:
    @staticmethod
    def from_file(reader):
        self = ByamlPathPoint()
        self.position = reader.read_vector_3d()
        self.normal = reader.read_vector_3d()
        self.unknown = reader.read_uint32()
        return self

    def __init__(self):
        self.position = None
        self.normal = None
        self.unknown = None