const fs = require("fs");
const path = require("path");
// copy srcdir to destdir sequentially and recursively
function copyTreeSeq(srcdir, destdir, callback) {
    fs.mkdir(destdir, function (err) {
        if (err) throw new Error(err);
        fs.readdir(srcdir, function (err, files) {
            if (err) throw new Error(err);
            (function loop(i) {
                function next(err) {
                    if (err) throw new Error(err);
                    loop(i + 1);
                }

                if (i < files.length) {
                    const f = files[i];
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
                            copyTreeSeq(fullname, dest, next);
                        } else if (stat.isFile()) {
                            fs.readFile(fullname, function (err, data) {
                                if (err) throw new Error(err);
                                fs.writeFile(dest, data, next);
                            });
                        } else {
                            next();
                        }
                    });
                } else {
                    callback();
                }
            })(0);
        });
    });
}

console.time("copyTreeSeq");
copyTreeSeq('./foo', '/tmp/test', function () {
    // rest of the program goes here.
    console.timeEnd("copyTreeSeq");
});
