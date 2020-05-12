/* Read javascript code from stdin and execute it.

 */
let STACKLEN = false;
function GUARD(args, f) {
    if (--STACKLEN < 0) throw new Continuation(f, args);
}

function Continuation(f, args) {
    this.f = f;
    this.args = args;
}

function Execute(f, args) {
    // console.log('entering');
    // if (IN_EXECUTE)
    // {
    //     console.log('here');
    //     return f.apply(null, args);
    // }
    // IN_EXECUTE = true;
    while (true)
        try {
            STACKLEN = 200;
            f.apply(null, args);
            break;
        } catch (ex) {
            if (ex instanceof Continuation) {
                f = ex.f;
                args = ex.args;
            } else {
                // IN_EXECUTE = false;
                throw ex;
            }
        }
    // IN_EXECUTE = false;
}

if (typeof process != "undefined") (function () {
    let code = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("readable", function () {
        const chunk = process.stdin.read();
        if (chunk) code += chunk;
    });
    process.stdin.on("end", function () {
        const func = new Function("β_TOPLEVEL, GUARD, Execute, require", code);
        // console.log(func.toString());
        console.error("/*");
        console.time("Runtime");
        Execute(func, [
            function (result) {
                console.timeEnd("Runtime");
                console.error("***Result: " + result);
                console.error("*/");
            },
            GUARD,
            Execute,
            require,
        ]);
        // result = eval(code);
        // console.log("The result is " + result)
    });
})();
