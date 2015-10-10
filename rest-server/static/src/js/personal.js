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

        // render data
        render: function(re) {
            //jq('html, body, #loadNext').css('background-color', '#ebebeb')
            //jq('html, body').css('background-color', '#f3f3f3')

            var headerHtml = template('tmpl_header', re.data),
                followHtml = template('tmpl_topicList', {
                    'data_list': re.data.follow_topics.data_list,
                    'count': re.data.follow_topics.count, 'title': '我的关注',
                    'link': '/following',
                    'icon': 'iconMark',
                }),
                topicHtml = template('tmpl_topicList', {
                    'data_list': re.data.publish_topics.data_list,
                    'count': re.data.publish_topics.count,
                    'title': '发表的话题',
                    'link': '/publish_topics',
                    'icon': 'iconTopic',
                });
                opinionHtml = template('tmpl_opinionList', {
                    'data_list': re.data.publish_opinions.data_list,
                    'count': re.data.publish_opinions.count,
                    'title': '我的看法',
                    'link': '/publish_opinions',
                    'icon': 'iconOpinion',
                });

            jq('#header').append(headerHtml);
            jq('#follow').append(followHtml);
            jq('#topic').append(topicHtml);
            jq('#opinion').append(opinionHtml);

            jq('.warp').show()
            //jq('.warp, #bottomBar').show()
            //jq('.warp, #bottomBar, .recommendTitle').show()

        },

        init: function() {
            var loadOpts = {
                isList: false,
                isEmptyShow: false,
                url: '/user',
                emptyCon: '',
                callback: exports.render,
            };

            thread.load(loadOpts, 'drag');
            initLazyload('.warp img');

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
