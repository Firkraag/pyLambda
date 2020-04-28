/* primitive for lambda
 */
print = function (txt) {
    this.console.log(txt);
};
println = function (txt) {
    this.console.log(txt);
};
fibpy = function (n) {
    if (n < 2) {
        return n;
    }
    else {
        return fibpy(n - 1) + fibpy(n - 2);
    }
};
time = function (func) {
    console.time('timing')
    var result = func();
    console.timeEnd('timing')
    return result;
};
