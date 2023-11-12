class JointDict:
    def __init__(self):
        self.forward_dict = {}
        self.reverse_dict = {}

        self.add_mapping("LEFT_ARM", {"11", "13", "15"})
        self.add_mapping("RIGHT_ARM", {"12", "14", "16"})

    def add_mapping(self, key, value):
        value_tuple = tuple(value)
        self.forward_dict[key] = value_tuple
        self.reverse_dict[value_tuple] = key

    def get_forward(self, key):
        key_tuple = tuple(key)
        return self.forward_dict.get(key_tuple, None)

    def get_reverse(self, value):
        value_tuple = tuple(value)
        return self.reverse_dict.get(value_tuple, None)


shared_joint_dict = JointDict()
