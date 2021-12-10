const ZergInterpreter = require('./static/plugin_prask_8_1_1/components/interpreter.js');
const Program = require('./static/plugin_prask_8_1_1/components/parser.js');
const readFileSync = require('fs').readFileSync;

function nop() {}

const data = JSON.parse(readFileSync(0, 'utf-8'));
const zergint = new ZergInterpreter(new Program(data.programRaw), data.level, nop, nop, nop, nop, nop, nop)

let status = zergint.SIM_OK
do {
    status = zergint.programStep()
} while (status == zergint.SIM_OK)

let exitcode = 0
if (status == zergint.SIM_LEVEL_PASSED) {
    exitcode = 0
} else {
    exitcode = 1
}

process.exit(exitcode)
