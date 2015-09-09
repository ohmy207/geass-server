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
        isLoadingNew: true,
        isLoading: false,
        isNoShowToTop: false,
        desc: 0,
        nextStart: 0,
        listType: 'topics',

        // load data,all in one
        load: function(start, action) {
            start = start || 0;
            action = action || '';

            exports.isLoading = true;
            /**
             * thread.js里调用，发表时新回复时，倒序，新发表的显示在最上面，正序在最下面
             */
            var desc = window.desc = exports.desc;
            var url = '/user/news/' + exports.listType
                + '?skip=' + start;

            var opts = {
                'beforeSend': function() {
                    switch(action) {
                        case 'pull':
                            jq('#refreshWait').show();
                            jq('#showAll').hide();
                            exports.isLoadingNew = true;
                            break;
                        case 'drag':
                            jq('#loadNext').show();
                            exports.isLoadingNew = true;
                            break;
                        case 'sort':
                            jq('#showAll').hide();
                            exports.isLoadingNew = true;
                            jQuery.UTIL.showLoading();
                            break;
                        default:
                            jq.UTIL.showLoading();
                    }
                },
                'complete': function() {
                },
                'success': function(re) {
                    jq('#refreshWait').hide();
                    jq('#loadNext').hide();
                    jq.UTIL.showLoading('none');
                    if (re.code == 0) {
                        exports.renderList(re, !start);
                    } else {
                        jq.UTIL.dialog({content: '拉取数据失败，请重试', autoClose: true});
                    }
                    exports.isLoading = false;
                }
            };
            jq.UTIL.ajax(url, '', opts);
        },

        // render data
        renderList: function(re, clear) {
            if (clear) {
                jq('#list').html('');
            }

            // 最后无数据不再加载
            if (jq.UTIL.isObjectEmpty(re.data.dataList)) {
                exports.isLoadingNew = false;
                jq('#loadNext').hide();
                //jq('#showAll').show();
                if (clear) {
                    jq('.emptyList').html('还没有看法哦^…^').show()
                }
                return true;
            }
            //re.data.isWX = isWX;
            var tmplId = 'tmpl_' + exports.listType;
            var listHtml = template(tmplId, re.data);

            jq('#list').append(listHtml);

            jq('#loadNext').hide();
            exports.nextStart = re.data.nextStart;
        },

        init: function() {
            var tId = window.tId;

            // 分享遮罩，一次性
            var action = jq.UTIL.getQuery('action');
            var reapp = /qqdownloader\/([^\s]+)/i;

            exports.load(exports.nextStart, 'drag');

            initLazyload('.warp img');

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
                        author = thisObj.attr('author');
                        thread.reply(tId, toCoId, author, 'comment');
                    }
                };
                thread.checkIsRegistered(callback);
            });

            exports.nextStart = window.nextStart;

            var level = /Android 4.0/.test(window.navigator.userAgent) ? -10 : -100;
            // 全屏触摸
            jq.UTIL.initTouch({
                obj: jq('.warp')[0],
                end: function(e, offset) {
                    document.ontouchmove = function(e){ return true;}
                    var loadingObj = jq('#loadNext');
                    var loadingPos = jq('#loadNextPos');
                    // var loadingObjTop = loadingObj.offset().top + loadingObj.height() - jq(window).scrollTop();
                    var loadingObjTop = loadingPos.offset().top - document.body.scrollTop - window.screen.availHeight;
                    // 向上滑
                    if (offset.y > 10 && loadingObjTop <= 10 && exports.isLoadingNew && !exports.isLoading) {
                        exports.load(exports.nextStart, 'drag');
                    }
                    // 向下拉刷新
                    if (offset.y < level && document.body.scrollTop <= 0) {
                    }
                }
            });

            jq('.warp').on('click', '.topicWrap', function(e) {
                jq.UTIL.touchStateNow(jq(this).parent('li'));
                jq.UTIL.reload(jq(this).data('link'));
            });

            jq('.groupBtn').on('click', 'li', function(e) {
                jq('.groupBtn').children('.selected').attr('class', '')
                jq(this).attr('class', 'selected');

                jq('#list').html('');
                exports.nextStart = 0;
                exports.listType = jq(this).attr('id')
                exports.load(exports.nextStart, 'drag');
            });

        },

    };

    exports.init();

});
