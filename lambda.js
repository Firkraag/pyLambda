/* Read javascript code from stdin and execute it.

 */
let STACKLEN, IN_EXECUTE = false;
function GUARD(args, f) {
    if (--STACKLEN < 0) throw new Continuation(f, args);
}
function Continuation(f, args) {
    this.f = f;
    this.args = args;
}
function Execute(f, args) {
    if (IN_EXECUTE)
        return f.apply(null, args);
    IN_EXECUTE = true;
    while (true) try {
        STACKLEN = 200;
        f.apply(null, args);
        break;
    } catch (ex) {
        if (ex instanceof Continuation) {
            f = ex.f;
            args = ex.args;
        } else {
            IN_EXECUTE = false;
            throw ex;
        }
    }
    IN_EXECUTE = false;
}
if (typeof process != "undefined") (function () {
    let code = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("readable", function () {
        const chunk = process.stdin.read();
        if (chunk) code += chunk;
    });
    process.stdin.on("end", function () {
        const func = new Function("β_TOPLEVEL, GUARD, Execute", code);
        console.log(func.toString());
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
        ]);
        // result = eval(code);
        // console.log("The result is " + result)
    });
})();
