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
        filterType: 'reply',

        load: function(action) {
            thread.load({
                isList: true,
                isEmptyShow: true,
                url: '/user/notifications',
                emptyCon: '还没有消息',
                type: exports.filterType,
                callback: exports.renderList,
            }, action);
        },

        // render data
        renderList: function(re, clear) {
            if (clear && re.data.has_new_support) {
                jq('.switchBar .notiNumber').show();
            }

            var listHtml = template('tmpl_noticeList', re.data);
            if(jq.trim(listHtml)!=='') {
                jq('#list').append(listHtml);
            }
        },

        init: function() {
            var tId = window.tId,
                loadOpts = {
                    isList: false,
                    isEmptyShow: true,
                    url: '/user/notifications?skip=0',
                    emptyCon: '还没有消息',
                    type: exports.filterType,
                    callback: exports.renderList,
                };

            thread.load(loadOpts, 'drag');
            initLazyload('.warp img');
            thread.initWeixin();

            // 回复楼中楼
            jq('.warp').on('click', '.replyFloor', function(e) {
                var thisObj = jq(this);

                // 获取帖子id
                var divId = thisObj.attr('id'), author;

                var callback = function() {
                    if (/co_[0-9a-f]{24}/.test(divId)) {
                        if (match = divId.match(/co_([0-9a-f]{24})/)) {
                            toCoId = match[1];
                        }

                        e.stopPropagation();
                        jq.UTIL.touchStateNow(thisObj);

                        tId = thisObj.attr('tid');
                        pId = thisObj.attr('pid');
                        author = thisObj.attr('author');
                        thread.reply(tId, pId, toCoId, author, 'comment');
                    }
                };
                thread.checkIsRegistered(callback);
            });

            thread.initTouchRefresh(exports.load);

            jq('.warp').on('click', '.topicWrap', function(e) {
                jq.UTIL.touchStateNow(jq(this).parent('li'));
                jq.UTIL.reload(jq(this).data('link'));
            });

            jq('.groupBtn').on('click', 'li', function(e) {
                jq('.groupBtn').children('.selected').attr('class', '')
                jq(this).attr('class', 'selected');
                jq('.switchBar .notiNumber').hide();

                jq('.emptyList').hide()
                jq('#list').html('');
                thread.nextStart = 0;
                exports.filterType = jq(this).attr('id')
                exports.load('drag');
            });

        },

    };

    exports.init();

});
