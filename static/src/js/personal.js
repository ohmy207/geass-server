/**
 **/

require.config({

    waitSeconds: 15,
    urlArgs: "t=" + (new Date()).getTime(),

    paths: {

        //"jquery": "vendor/jquery-1.11.2.min",
        "jquery": "vendor/jquery.min",
        "art-template": "vendor/art-template",
        "util": "module/util",

        "jpegMeta": "module/jpegMeta",
        "JPEGEncoder": "module/JPEGEncoder",
        "imageCompresser": "module/imageCompresser",
        "uploadImg": "module/uploadImg",
        "thread": "module/thread",
    }

});

require(['art-template', 'util', 'thread'],function (template, util, thread){

    var exports = {
        isNoShowToTop: false,

        // render data
        render: function(re) {
            //jq('html, body, #loadNext').css('background-color', '#ebebeb')
            //jq('html, body').css('background-color', '#f3f3f3')

            var followHtml = template('tmpl_topicList', {'dataList': re.data.follow.data_list, 'count': re.data.follow.count, 'title': '我的关注', 'link': '/following'}),
                headerHtml = template('tmpl_header', re.data),
                publishHtml = template('tmpl_topicList', {'dataList': re.data.publish.data_list, 'count': re.data.publish.count, 'title': '发表的话题', 'link': '/publishing'});

            jq('#header').append(headerHtml);
            jq('#follow').append(followHtml);
            jq('#publish').append(publishHtml);

            jq('.warp').show()
            //jq('.warp, #bottomBar').show()
            //jq('.warp, #bottomBar, .recommendTitle').show()

        },

        init: function() {
            var tId = window.tId,
                loadOpts = {
                    isList: false,
                    isEmptyShow: false,
                    url: '/user',
                    emptyCon: '',
                    callback: exports.render,
                };

            thread.load(loadOpts, 'drag');

            initLazyload('.warp img');

            jq('.warp, #bottomBar').on('click', '.threadReply', function() {
                var thisObj = jq(this);
                thread.reply(tId, null, '', 'proposal');
            });

            jq('.warp').on('click', '.pTitle', function(e) {
                jq.UTIL.touchStateNow(jq(this));
                jq.UTIL.reload(jq(this).data('link'));
            });

            jq('.warp').on('click', '.topicWrap', function(e) {
                jq.UTIL.touchStateNow(jq(this).parent('li'));
                jq.UTIL.reload(jq(this).data('link'));
            });

        },

    };

    exports.init();

});
