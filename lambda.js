/* Read javascript code from stdin and execute it.

 */
if (typeof process != "undefined") (function () {
    var code = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("readable", function () {
        var chunk = process.stdin.read();
        if (chunk) code += chunk;
    });
    process.stdin.on("end", function () {
        result = eval(code);
        print("The result is " + result)
    });
})();
