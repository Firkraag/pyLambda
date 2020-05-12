const fs = require("fs");
const path = require("path");

function copyTree(srcdir, destdir, callback) {
    fs.mkdir(destdir, function (err) {
        if (err) throw new Error(err);
        fs.readdir(srcdir, function (err, files) {
            if (err) throw new Error(err);
            let count = files.length;

            function next(err) {
                if (err) throw new Error(err);
                if (--count === 0) callback();
            }

            if (count === 0) {
                callback();
            } else {
                files.forEach(function (f) {
                    const fullname = path.join(srcdir, f);
                    const dest = path.join(destdir, f);
                    fs.lstat(fullname, function (err, stat) {
                        if (err) throw new Error(err);
                        if (stat.isSymbolicLink()) {
                            fs.readlink(fullname, function (err, target) {
                                if (err) throw new Error(err);
                                fs.symlink(target, dest, next);
                            });
                        } else if (stat.isDirectory()) {
                            copyTree(fullname, dest, next);
                        } else if (stat.isFile()) {
                            fs.readFile(fullname, function (err, data) {
                                if (err) throw new Error(err);
                                fs.writeFile(dest, data, next);
                            });
                        } else {
                            next();
                        }
                    });
                });
            }
        });
    });
}

console.time("copyTreeParallel");
copyTree('./foo', '/tmp/test', function () {
    // rest of the program goes here.
    console.timeEnd("copyTreeParallel");
});
