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
        "opinion": "opinion",
        "comment": "comment",
        "personal": "personal",
        "personal_list": "personal_list",
        "proposal_list": "proposal_list",
        "news_list": "news_list",
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
            name: "opinion",
        },
        {
            name: "comment",
        },
        {
            name: "personal",
        },
        {
            name: "personal_list",
        },
        {
            name: "proposal_list",
        },
        {
            name: "news_list",
        },
    ],
    //fileExclusionRegExp: /^(?:module|vendor|(?:r|build)\.js)$/,
    fileExclusionRegExp: /^(?:r|build|jquery\.lazyloadxt\.min|jquery\-1\.11\.2\.min)\.js$/,
    removeCombined: true,
})
