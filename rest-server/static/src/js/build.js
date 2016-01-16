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
        "home": "home",
        "detail": "detail",
        "proposal": "proposal",
        "opinion": "opinion",
        "comment": "comment",
        "personal": "personal",
        "personal_list": "personal_list",
        "notice_list": "notice_list",
    },
    shim:{
        "util": ['jquery', 'vendor/jquery.form.min'],
    },
    modules: [
        {
            name: "new",
            exclude: ["util"]
        },
        {
            name: "home",
            exclude: ["util"]
        },
        {
            name: "detail",
            exclude: ["util"]
        },
        {
            name: "proposal",
            exclude: ["util"]
        },
        {
            name: "opinion",
            exclude: ["util"]
        },
        {
            name: "comment",
            exclude: ["util"]
        },
        {
            name: "personal",
            exclude: ["util"]
        },
        {
            name: "personal_list",
            exclude: ["util"]
        },
        {
            name: "notice_list",
            exclude: ["util"]
        },
        {
            name: "util",
        },
    ],
    //fileExclusionRegExp: /^(?:module|vendor|(?:r|build)\.js)$/,
    fileExclusionRegExp: /^(?:r|build|jquery\.lazyloadxt\.min|jquery\-1\.11\.2\.min)\.js$/,
    removeCombined: true,
})
