/* primitive for lambda
 */
print = function (txt) {
    this.console.log(txt);
};
println = function (txt) {
    this.console.log(txt);
};
fibPY = function (n) {
    if (n < 2) {
        return n;
    }
    else {
        return fibPY(n - 1) + fibPY(n - 2);
    }
};
time = function (func) {
    console.time('timing')
    var result = func();
    console.timeEnd('timing')
    return result;
};
