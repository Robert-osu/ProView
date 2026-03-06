from Command import Command

cmd_list = list(Command)


# Для ONE_ARGS команд
one_args_config = {
    cmd_list[97]:  (34, 44, 1),
    cmd_list[98]:  (28, 44, 1),
    cmd_list[104]: (32, 48, 1),
    cmd_list[105]: (32, 48, 1),
    cmd_list[106]: (32, 50, 1),
    cmd_list[107]: (32, 48, 1),
    cmd_list[112]: (35, 42, 1),
    cmd_list[113]: (35, 42, 1),
    cmd_list[114]: (35, 40, 1),
    cmd_list[115]: (35, 40, 1),
    cmd_list[116]: (38, 40, 1),
    cmd_list[117]: (38, 40, 1),
    cmd_list[125]: (30, 33, 1),
    cmd_list[126]: (30, 33, 1),
    cmd_list[127]: (30, 33, 1),
    cmd_list[24]:  (42, 33, None),  # type не указан
    cmd_list[25]:  (32, 33, None),
    cmd_list[26]:  (32, 33, None),
    cmd_list[40]:  (20, 33, None),
    cmd_list[166]: (30, 52, None),
    cmd_list[137]: (32, 33, None),
    cmd_list[139]: (28, 52, None),
    cmd_list[140]: (28, 52, None),
    cmd_list[181]: (30, 35, None),
    cmd_list[182]: (30, 35, None),
}

# Для TWO_ARGS команд - создадим вложенную структуру
two_args_config = {
    'above': {  # когда self.y + 32 > mouse_y
        cmd_list[119]: (22, 23, None),
        cmd_list[99]:  (30, 15, 2),
        cmd_list[100]: (30, 15, 2),
        cmd_list[101]: (30, 15, 2),
        cmd_list[102]: (30, 15, 2),
        cmd_list[103]: (30, 15, 2),
        cmd_list[120]: (22, 23, None),
        cmd_list[121]: (22, 23, None),
        cmd_list[122]: (22, 23, None),
        cmd_list[123]: (22, 23, None),
        cmd_list[124]: (22, 23, None),
        cmd_list[108]: (26, 16, None),
        cmd_list[109]: (26, 16, None),
        cmd_list[110]: (26, 16, None),
        cmd_list[111]: (26, 16, None),
        cmd_list[128]: (22, 22, None),
        cmd_list[129]: (22, 22, None),
        cmd_list[130]: (22, 22, None),
    },
    'below': {  # когда self.y + 32 <= mouse_y
        cmd_list[119]: (30, 52, None),
        cmd_list[99]:  (32, 50, None),
        cmd_list[100]: (32, 50, None),
        cmd_list[101]: (32, 50, None),
        cmd_list[102]: (32, 50, None),
        cmd_list[103]: (32, 50, None),
        cmd_list[120]: (30, 52, None),
        cmd_list[121]: (30, 52, None),
        cmd_list[122]: (30, 52, None),
        cmd_list[123]: (30, 52, None),
        cmd_list[124]: (30, 52, None),
        cmd_list[108]: (30, 50, None),
        cmd_list[109]: (30, 50, None),
        cmd_list[110]: (30, 50, None),
        cmd_list[111]: (30, 50, None),
        cmd_list[128]: (30, 50, None),
        cmd_list[129]: (38, 50, None),
        cmd_list[130]: (38, 50, None),
    }
}

class CommandConfig:
    ### x, y, type: тип вводимого значения: 0метка/1переменная/2значение
    def __init__(self):
        self.cmd_list = list(Command)
        self._init_one_args_config()
        self._init_two_args_config()
    
    def _init_one_args_config(self):
        self.one_args = {
            cmd_list[97]:  (34, 44, 1),
            cmd_list[98]:  (28, 44, 1),
            cmd_list[104]: (32, 48, 1),
            cmd_list[105]: (32, 48, 1),
            cmd_list[106]: (32, 50, 1),
            cmd_list[107]: (32, 48, 1),
            cmd_list[112]: (35, 42, 1),
            cmd_list[113]: (35, 42, 1),
            cmd_list[114]: (35, 40, 1),
            cmd_list[115]: (35, 40, 1),
            cmd_list[116]: (38, 40, 1),
            cmd_list[117]: (38, 40, 1),
            cmd_list[125]: (30, 33, 1),
            cmd_list[126]: (30, 33, 1),
            cmd_list[127]: (30, 33, 1),
            cmd_list[24]:  (42, 33, 0),  
            cmd_list[25]:  (32, 33, 0),
            cmd_list[26]:  (32, 33, 0),
            cmd_list[40]:  (20, 33, 0),
            cmd_list[166]: (30, 52, 0),
            cmd_list[137]: (32, 33, 0),
            cmd_list[139]: (28, 52, 0),
            cmd_list[140]: (28, 52, 0),
            cmd_list[181]: (30, 35, 0),
            cmd_list[182]: (30, 35, 0),
        }
        self.one_args_default = (30, 33, 0)
    
    def _init_two_args_config(self):
        self.two_args_above = {
            cmd_list[119]: (22, 23, 1),
            cmd_list[99]:  (30, 15, 2),
            cmd_list[100]: (30, 15, 2),
            cmd_list[101]: (30, 15, 2),
            cmd_list[102]: (30, 15, 2),
            cmd_list[103]: (30, 15, 2),
            cmd_list[120]: (22, 23, 1),
            cmd_list[121]: (22, 23, 1),
            cmd_list[122]: (22, 23, 1),
            cmd_list[123]: (22, 23, 1),
            cmd_list[124]: (22, 23, 1),
            cmd_list[108]: (26, 16, 1),
            cmd_list[109]: (26, 16, 1),
            cmd_list[110]: (26, 16, 1),
            cmd_list[111]: (26, 16, 1),
            cmd_list[128]: (22, 22, 1),
            cmd_list[129]: (22, 22, 1),
            cmd_list[130]: (22, 22, 1),
        }
        self.two_args_below = {
            cmd_list[119]: (30, 52, 2),
            cmd_list[99]:  (32, 50, 1),
            cmd_list[100]: (32, 50, 1),
            cmd_list[101]: (32, 50, 1),
            cmd_list[102]: (32, 50, 1),
            cmd_list[103]: (32, 50, 1),
            cmd_list[120]: (30, 52, 2),
            cmd_list[121]: (30, 52, 2),
            cmd_list[122]: (30, 52, 2),
            cmd_list[123]: (30, 52, 2),
            cmd_list[124]: (30, 52, 2),
            cmd_list[108]: (30, 50, 1),
            cmd_list[109]: (30, 50, 1),
            cmd_list[110]: (30, 50, 1),
            cmd_list[111]: (30, 50, 1),
            cmd_list[128]: (30, 50, 2),
            cmd_list[129]: (38, 50, 1),
            cmd_list[130]: (38, 50, 1),
        }
        self.two_args_above_default = (30, 15, 1)
        self.two_args_below_default = (32, 50, 1)
    
    def get_one_args_config(self, cmd):
        return self.one_args.get(cmd, self.one_args_default)
    
    def get_two_args_config(self, cmd, is_above):
        if is_above:
            return self.two_args_above.get(cmd, self.two_args_above_default)
        else:
            return self.two_args_below.get(cmd, self.two_args_below_default)
        
    def get(self, cmd, is_above=True):
        if cmd in Command.NO_ARGS:
            return (None, None, None)
        elif cmd in Command.ONE_ARGS:
            return self.get_one_args_config(cmd)
        elif cmd in Command.TWO_ARGS:
            return self.get_two_args_config(cmd, not is_above)