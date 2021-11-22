export var Program = function(program) {

    this.subroutines = {};
    this.errors = [];

    var check_function_calls = [];

    var lines = program.split(/\r?\n|\r/);
    var instructions = [];
    var current_subroutine = "main";

    for (var i = 0; i < lines.length; i++) {

        if (lines[i].search(/aha funkcia[0-9]:/) != -1) {
            this.subroutines[current_subroutine] = new this.Subroutine(current_subroutine, instructions);
            instructions = [];
            current_subroutine = "sub" + lines[i].match(/[0-9]/)[0];
            continue;
        }

        var states = {
            command:                    1,
            eol_or_if:                  2,
            parentheses_not_condition:  3,
            logic_endparentheses:       5,
            wall_modifier:              7,
            end:                        8
        };
        var state = states.command;

        var tokens = lines[i].replace(/\(/g, ' ( ').replace(/\)/g, ' ) ').split(' ');

        var sub_num = null;
        var opcode = null;
        var conditions = [];
        var negation_stack = [];
        var negate = false;
        var previous_op_was_not = false;
        var error = null;

        var last_processed_token = 0;

        for (var j = 0; j < tokens.length && state != states.end; j++) {
            if (tokens[j] === "" || tokens[j] === "je") {
                continue;
            }
            switch (state) {
                case states.command:
                    switch(tokens[j]) {
                        case "krok":
                            opcode = this.OPCODE_WALK;
                            state = states.eol_or_if;
                            break;
                        case "doprava":
                            opcode = this.OPCODE_TURN_RIGHT;
                            state = states.eol_or_if;
                            break;
                        case "dolava":
                            opcode = this.OPCODE_TURN_LEFT;
                            state = states.eol_or_if;
                            break;
                        case "prepni":
                            opcode = this.OPCODE_TOGGLE;
                            state = states.eol_or_if;
                            break;
                        default:
                            if (tokens[j].search(/funkcia[0-9]/) != -1) {
                                sub_num = tokens[j].match(/[0-9]/)[0];
                                opcode = this.OPCODE_SUB0 + parseInt(sub_num);
                                state = states.eol_or_if;
                                check_function_calls.push({'func': 'sub' + tokens[j].match(/[0-9]/)[0], 'line': i});
                            } else {
                                error = new this.BotSyntaxError("Neznámy príkaz \"" + tokens[j] + "\".", i);
                                state = states.end;
                            }
                    }
                    break;
                case states.eol_or_if:
                    if (tokens[j] === "ak") {
                        state = states.parentheses_not_condition;
                    } else {
                        error = new this.BotSyntaxError("Za príkazom musí byť koniec riadku alebo \"ak\". Je tam \"" + tokens[j] + "\".", i);
                        state = states.end;
                    }
                    break;
                case states.parentheses_not_condition:
                    switch(tokens[j]) {
                        case "(":
                            negation_stack.push(negate);
                            if (previous_op_was_not === true) {
                                negate = !negate;
                                previous_op_was_not = false;
                            }
                            conditions.push(this.LOGIC_PAR_LEFT);
                            break;
                        case "nie":
                            previous_op_was_not = !previous_op_was_not;
                            break;
                        case "svieti":
                            var neg = false;
                            if (previous_op_was_not) neg = !neg;
                            if (negate) neg = !neg;
                            if (neg === false) {
                                conditions.push(this.CONDITION_LIT);
                            } else {
                                conditions.push(this.CONDITION_NOTLIT);
                            }
                            previous_op_was_not = false;
                            state = states.logic_endparentheses;
                            break;
                        case "nesvieti":
                            var neg = false;
                            if (previous_op_was_not) neg = !neg;
                            if (negate) neg = !neg;
                            if (neg === false) {
                                conditions.push(this.CONDITION_NOTLIT);
                            } else {
                                conditions.push(this.CONDITION_LIT);
                            }
                            previous_op_was_not = false;
                            state = states.logic_endparentheses;
                            break;
                        case "stena":
                            state = states.wall_modifier;
                            break;
                        default:
                            error = new this.BotSyntaxError('Za \"' + tokens[last_processed_token] + '\" očakávam zátvorku, \"nie\" alebo podmienku.', i);
                            state = states.end;
                            break;
                    }
                    break;
                case states.logic_endparentheses:
                    switch(tokens[j]) {
                        case "a":
                            if (negate) conditions.push(this.LOGIC_OR);
                            else conditions.push(this.LOGIC_AND);
                            state = states.parentheses_not_condition;
                            break;
                        case "alebo":
                            if (!negate) conditions.push(this.LOGIC_OR);
                            else conditions.push(this.LOGIC_AND);
                            state = states.parentheses_not_condition;
                            break;
                        case ")":
                            if (negation_stack.length > 0) {
                                negate = negation_stack.pop();
                                conditions.push(this.LOGIC_PAR_RIGHT);
                                state = states.logic_endparentheses;
                            } else {
                                error = new this.BotSyntaxError("Nezhodujúce sa zátvorky!", i);
                                state = states.end;
                            }
                            break;
                        default:
                            error = new this.BotSyntaxError('Za \"' + tokens[last_processed_token] + '\" očakávam logickú spojku alebo koniec zátvorky.', i);
                            state = states.end;
                            break;
                    }
                    break;
                case states.wall_modifier:
                    var neg = false;
                    if (previous_op_was_not) neg = !neg;
                    if (negate) neg = !neg;
                    switch(tokens[j]) {
                        case "vpravo":
                            if (neg) conditions.push(this.CONDITION_NOWALL_RIGHT);
                            else conditions.push(this.CONDITION_WALL_RIGHT);
                            previous_op_was_not = false;
                            state = states.logic_endparentheses;
                            break;
                        case "vlavo":
                            if (neg) conditions.push(this.CONDITION_NOWALL_LEFT);
                            else conditions.push(this.CONDITION_WALL_LEFT);
                            previous_op_was_not = false;
                            state = states.logic_endparentheses;
                            break;
                        case "vpredu":
                            if (neg) conditions.push(this.CONDITION_NOWALL_FRONT);
                            else conditions.push(this.CONDITION_WALL_FRONT);
                            previous_op_was_not = false;
                            state = states.logic_endparentheses;
                            break;
                        case "vzadu":
                            if (neg) conditions.push(this.CONDITION_NOWALL_BACK);
                            else conditions.push(this.CONDITION_WALL_BACK);
                            previous_op_was_not = false;
                            state = states.logic_endparentheses;
                            break;
                        default:
                            error = new this.BotSyntaxError('Za \"' + tokens[last_processed_token] + '\" očakávam \"vpravo\", \"vlavo\", \"vpredu\" alebo \"vzadu\".', i);
                            state = states.end;
                            break;
                    }
                    break;
            }
            last_processed_token = j;
        }

        switch(state) {
            case states.parentheses_not_condition:
                error = new this.BotSyntaxError("Neočakávaný koniec riadku. Očakávam zátvorku, \"nie\" alebo podmienku.", i);
                break;
            case states.parentheses_condition:
                error = new this.BotSyntaxError("Neočakávaný koniec riadku. Očakávam zátvorku alebo podmienku.", i);
                break;
            case states.not_condition:
                error = new this.BotSyntaxError("Neočakávaný koniec riadku. Očakávam \"nie\" alebo podmienku.", i);
                break;
            case states.wall_modifier:
                error = new this.BotSyntaxError("Neočakávaný koniec riadku. Očakávam \"vpravo\", \"vlavo\", \"vpredu\" alebo \"vzadu\".", i);
                break;
        }

        if (negation_stack.length != 0 && error == null) {
            error = new this.BotSyntaxError("Nezhodujúce sa zátvorky!", i);
        }

        if (error != null) {
            this.errors.push(error);
        } else if (opcode != null) {
            instructions.push(new this.Instruction(opcode, conditions, i));
        }
    }

    this.subroutines[current_subroutine] = new this.Subroutine(current_subroutine, instructions);

    for (var i = 0; i < check_function_calls.length; i++) {
        if (this.subroutines[check_function_calls[i].func] == undefined) {
            this.errors.push(new this.BotSyntaxError("Nedefinovaná funkcia. Môžeš ju definovať pomocou \"aha\".", check_function_calls[i].line));
        }
    }
};

Program.prototype = {
    Instruction: function(opcode, condition, original_line) {
        this.opcode = opcode;
        this.condition = condition;
        this.original_line = original_line;
    },
    Subroutine: function(name, instructions) {
        this.name = name;
        this.instructions = instructions;
    },
    BotSyntaxError: function(description, original_line) {
        this.description = description;
        this.original_line = original_line;
    },
    OPCODE_WALK:            0,
    OPCODE_TURN_RIGHT:      1,
    OPCODE_TURN_LEFT:       2,
    OPCODE_TOGGLE:          3,
    OPCODE_SUB_MAIN:        4,
    OPCODE_SUB0:            5,
    OPCODE_SUB1:            6,
    OPCODE_SUB2:            7,
    OPCODE_SUB3:            8,
    OPCODE_SUB4:            9,
    OPCODE_SUB5:            10,
    OPCODE_SUB6:            11,
    OPCODE_SUB7:            12,
    OPCODE_SUB8:            13,
    OPCODE_SUB9:            14,
    LOGIC_AND:              28,
    LOGIC_OR:               15,
    CONDITION_LIT:          16,
    CONDITION_NOTLIT:       17,
    CONDITION_WALL_FRONT:   18,
    CONDITION_WALL_LEFT:    19,
    CONDITION_WALL_BACK:    20,
    CONDITION_WALL_RIGHT:   21,
    CONDITION_NOWALL_FRONT: 22,
    CONDITION_NOWALL_LEFT:  23,
    CONDITION_NOWALL_BACK:  24,
    CONDITION_NOWALL_RIGHT: 25,
    LOGIC_PAR_LEFT:         26,
    LOGIC_PAR_RIGHT:        27
};
