export var ZergInterpreter = function(program, level, walkToCallback, rotateRightCallback, rotateLeftCallback, redrawCallback, highlightLineCallback, updateBatteryCallback) {
	this.program = program;
	this.level = level;
	this.walkToCallback = walkToCallback;
	this.rotateRightCallback = rotateRightCallback;
	this.rotateLeftCallback = rotateLeftCallback;
	this.redrawCallback = redrawCallback;
	this.highlightLineCallback = highlightLineCallback;
	this.updateBatteryCallback = updateBatteryCallback;

	this.program_counter = 0;
	this.line_counter = 0;
	this.program_stack = ["main"];
	this.counter_stack = [];
	this.botX = this.level.startX;
	this.botY = this.level.startY;
	this.botHeading = this.level.startFacing;
	this.remaining_battery = this.level.battery_limit;
	this.used_memory = 0;

	this.level.recalculate_logic = function() {
            for (var x in this.torch_logic) {
                for (var y in this.torch_logic[x]) {
                    var value = false;
                    var operator = '|';
                    for (var op in this.torch_logic[x][y]) {
                        if (typeof(this.torch_logic[x][y][op]) == "object") {
                            var negate = this.torch_logic[x][y][op].not;
                            var cur_val = this.logic_map[this.torch_logic[x][y][op].y][this.torch_logic[x][y][op].x];
                            switch(operator) {
                                case '|':
                                    value |= negate ? !cur_val : cur_val;
                                    break;
                                case '&':
                                    value &= negate ? !cur_val : cur_val;
                                    break;
                            }
                        } else {
                            operator = this.torch_logic[x][y][op];
                        }
                    }
                    this.logic_map[y][x] = value;
                }
            }
        }
}

ZergInterpreter.prototype = {

	SIM_OK: 0,
	SIM_NO_BATTERY: 1,
	SIM_DEAD_JETTORCH: 2,
	SIM_FINISHED: 3,
	SIM_LEVEL_PASSED: 4,

	programStep: function() {
		var instruction = this.program.subroutines[this.program_stack[this.program_stack.length - 1]].instructions[this.program_counter];

		this.line_counter = instruction.original_line;

		this.highlightLineCallback(this.line_counter);

		if (this.remaining_battery == 0) {
		    return this.SIM_NO_BATTERY;
		}
		this.remaining_battery--;

		this.updateBatteryCallback(this.remaining_battery);
		var execute = false;
		if (instruction.condition == null || instruction.condition.length == 0) {
		    execute = true;
		} else {
		    var expr_stack = [];
		    for (var i in instruction.condition) {
		        var condition = false;
		        var evaluated = false;
		        var check_heading = 0;
		        var heading_evaluated = false;
		        var negate_wall = false;
		        switch (instruction.condition[i]) {
		            case this.program.LOGIC_AND:
		            case this.program.LOGIC_OR:
		                expr_stack.push(instruction.condition[i]);
		                break;

		            case this.program.CONDITION_NOTLIT:
		                if (!evaluated) {
		                    condition = this.level.logic_map[this.botY][this.botX] == false;
		                    evaluated = true;
		                }
		                // break missing on purpose
		            case this.program.CONDITION_LIT:
		                if (!evaluated) {
		                    condition = this.level.logic_map[this.botY][this.botX] == true;
		                    evaluated = true;
		                }
		                // break missing on purpose

		            case this.program.CONDITION_NOWALL_BACK:
		                if (!heading_evaluated) {
		                    negate_wall = true;
		                }
		                //break missing on purpose
		            case this.program.CONDITION_WALL_BACK:
		                if (!heading_evaluated) {
		                    check_heading = this.botHeading + 2;
		                    check_heading %= 4;
		                    heading_evaluated = true;
		                }
		                // break missing on purpose
		            case this.program.CONDITION_NOWALL_FRONT:
		                if (!heading_evaluated) {
		                    negate_wall = true;
		                }
		                //break missing on purpose
		            case this.program.CONDITION_WALL_FRONT:
		                if (!heading_evaluated) {
		                    check_heading = this.botHeading;
		                    heading_evaluated = true;
		                }
		                // break missing on purpose

		            case this.program.CONDITION_NOWALL_LEFT:
		                if (!heading_evaluated) {
		                    negate_wall = true;
		                }
		                //break missing on purpose
		            case this.program.CONDITION_WALL_LEFT:
		                if (!heading_evaluated) {
		                    check_heading = this.botHeading + 3;
		                    check_heading %= 4;
		                    heading_evaluated = true;
		                }
		                // break missing on purpose

		            case this.program.CONDITION_NOWALL_RIGHT:
		                if (!heading_evaluated) {
		                    negate_wall = true;
		                }
		                //break missing on purpose
		            case this.program.CONDITION_WALL_RIGHT:
		                if (!heading_evaluated) {
		                    check_heading = this.botHeading + 1;
		                    check_heading %= 4;
		                    heading_evaluated = true;
		                }

		                if (!evaluated) {
		                    switch(check_heading) {
		                        case 0:
		                            condition = (this.botX+1 >= this.level.sizeX ||
		                                         this.level.map[this.botY][this.botX+1] == 'W');
		                            break;
		                        case 1:
		                            condition = (this.botY+1 >= this.level.sizeY ||
		                                         this.level.map[this.botY+1][this.botX] == 'W');
		                            break;
		                        case 2:
		                            condition = (this.botX-1 < 0 ||
		                                         this.level.map[this.botY][this.botX-1] == 'W');
		                            break;
		                        case 3:
		                            condition = (this.botY-1 < 0 ||
		                                         this.level.map[this.botY-1][this.botX] == 'W');
		                            break;
		                    }
		                    if (negate_wall) {
		                        condition = !condition;
		                    }
		                    evaluated = true;
		                }

		                if (expr_stack[expr_stack.length - 1] == this.program.LOGIC_AND ||
		                    expr_stack[expr_stack.length - 1] == this.program.LOGIC_OR) {
		                    var operation = expr_stack.pop();
		                    var left = expr_stack.pop();
		                    if (operation == this.program.LOGIC_AND) {
		                        expr_stack.push(left && condition);
		                    } else {
		                        expr_stack.push(left || condition);
		                    }
		                } else {
		                    expr_stack.push(condition);
		                }
		                break;
		            case this.program.LOGIC_PAR_LEFT:
		                expr_stack.push(instruction.condition[i]);
		                break;
		            case this.program.LOGIC_PAR_RIGHT:
		                switch(expr_stack[expr_stack.length - 1]) {
		                    case this.program.LOGIC_PAR_LEFT:
		                        expr_stack.pop();
		                        break;
		                    default:
		                        var right = expr_stack.pop();
		                        expr_stack.pop(); // Left parentheses
		                        var operation = expr_stack.pop();
		                        var left = expr_stack.pop();
		                        if (operation == this.program.LOGIC_AND) {
		                            expr_stack.push(left && right);
		                        } else {
		                            expr_stack.push(left || right);
		                        }
		                        break;
		                }
		                break;
		        }
		        execute = expr_stack[0];
		    }
		}

		if (execute) {
		    switch (instruction.opcode) {
		        case this.program.OPCODE_WALK:
		            var walk_possible = false;
		            switch (this.botHeading) {
		                case 0:
		                    walk_possible = !(this.botX+1 >= this.level.sizeX ||
		                                      this.level.map[this.botY][this.botX+1] == 'W');
		                    if (walk_possible) this.botX += 1;
		                    break;
		                case 1:
		                    walk_possible = !(this.botY+1 >= this.level.sizeY ||
		                                      this.level.map[this.botY+1][this.botX] == 'W');
		                    if (walk_possible) this.botY += 1;
		                    break;
		                case 2:
		                    walk_possible = !(this.botX-1 < 0 ||
		                                      this.level.map[this.botY][this.botX-1] == 'W');
		                    if (walk_possible) this.botX -= 1;
		                    break;
		                case 3:
		                    walk_possible = !(this.botY-1 < 0 ||
		                                      this.level.map[this.botY-1][this.botX] == 'W');
		                    if (walk_possible) this.botY -= 1;
		                    break;
		            }
		            this.walkToCallback(this.botX, this.botY);
		            break;

		        case this.program.OPCODE_TURN_RIGHT:
		            this.botHeading += 1;
		            this.botHeading %= 4;
		            this.rotateRightCallback();
		            break;

		        case this.program.OPCODE_TURN_LEFT:
		            this.botHeading -= 1;
		            if (this.botHeading == -1) this.botHeading = 3;
		            this.rotateLeftCallback();
		            break;

		        case this.program.OPCODE_TOGGLE:
		            if (this.level.map[this.botY][this.botX] == 'M') {
		                this.level.logic_map[this.botY][this.botX] = !this.level.logic_map[this.botY][this.botX];
		                this.level.recalculate_logic();
		                this.redrawCallback(this.level);
		            }
		            break;

		        case this.program.OPCODE_SUB0:
		        case this.program.OPCODE_SUB1:
		        case this.program.OPCODE_SUB2:
		        case this.program.OPCODE_SUB3:
		        case this.program.OPCODE_SUB4:
		        case this.program.OPCODE_SUB5:
		        case this.program.OPCODE_SUB6:
		        case this.program.OPCODE_SUB7:
		        case this.program.OPCODE_SUB8:
		        case this.program.OPCODE_SUB9:
		            this.program_stack.push("sub" + (instruction.opcode - this.program.OPCODE_SUB0));
		            this.counter_stack.push(this.program_counter + 1);
		            this.program_counter = -1;
		            break;
		    }

		}

		if (this.level.map[this.botY][this.botX] == 'J' && this.level.logic_map[this.botY][this.botX] == true) {
		    return this.SIM_DEAD_JETTORCH;
		} else if (this.level.map[this.botY][this.botX] == 'E') {
		    return this.SIM_LEVEL_PASSED;
		}

		this.program_counter++;
		while (this.program_counter >= this.program.subroutines[this.program_stack[this.program_stack.length - 1]].instructions.length) {
		    if (this.counter_stack.length === 0) {
		        return this.SIM_FINISHED;
		    }
		    this.program_counter = this.counter_stack.pop();
		    this.program_stack.pop();
		}

		return this.SIM_OK;
	}

}
