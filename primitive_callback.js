println = function (k, txt) {
    console.log(txt);
    return k(false);
};
print = function (k, txt) {
    process.stdout.write(txt);
    return k(false);
};
fibpy = function (k, n) {
    var result = (function fib(n) {
        if (n < 2)
            return n;
        else {
            return fib(n - 1) + fib(n - 2);
        }
    })(n);
    return k(result);
};
sum = function (k, a, b) {
    return k(a + b);
};
time = function (k, func, ...args) {
    // console.log(k, func, args);
    args = [function (result) {
        console.timeEnd("timing");
        return k(result);
    }].concat(args);
    console.time("timing");
    return func.apply(null, args);
};