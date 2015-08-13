({
    appDir: "./",
    baseUrl: "./",
    dir: "../../js",
    paths: {
        //"jquery": "vendor/jquery-1.11.2.min",
        "jquery": "vendor/jquery.min",
        "art-template": "vendor/art-template",
        "jquery.form": "vendor/jquery.form.min",

        "util": "module/util",
        "jpegMeta": "module/jpegMeta",
        "JPEGEncoder": "module/JPEGEncoder",
        "imageCompresser": "module/imageCompresser",
        "uploadImg": "module/uploadImg",
        "thread": "module/thread",

        "new": "new",
        "detail": "detail",
        "proposal": "proposal",
        "comment": "comment",
    },
    shim:{
        "util": ['jquery', 'vendor/jquery.form.min'],
    },
    modules: [
        {
            name: "new",
        },
        {
            name: "detail",
        },
        {
            name: "proposal",
        },
        {
            name: "comment",
        },
    ],
    //fileExclusionRegExp: /^(?:module|vendor|(?:r|build)\.js)$/,
    fileExclusionRegExp: /^(?:r|build|jquery\.lazyloadxt\.min|jquery\-1\.11\.2\.min)\.js$/,
    removeCombined: true,
})
