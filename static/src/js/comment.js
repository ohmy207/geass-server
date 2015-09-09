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

        // load data,all in one
        load: function(start, action) {
            start = start || 0;
            action = action || '';

            exports.isLoading = true;
            /**
             * thread.js里调用，发表时新回复时，倒序，新发表的显示在最上面，正序在最下面
             */
            var desc = window.desc = exports.desc;
            //var url = DOMAIN + window.sId + '/t/' + window.tId
            var url = '/topics/' + window.tId + '/comments'
                + '?skip=' + start
                //+ '&desc=' + desc;
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
                        var zero = new Date;
                        exports.renderList(re, !start);
                        //stat.reportPoint('listRender', 10, new Date, zero);
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
                jq('#allReplyList').html('');
            }

            // 最后无数据不再加载
            if (jq.UTIL.isObjectEmpty(re.data.dataList)) {
                exports.isLoadingNew = false;
                jq('#loadNext').hide();
                //jq('#showAll').show();
                return true;
            }
            //re.data.isWX = isWX;
            re.data.tmplType = 'hot';
            var hotReplyHtml = template('tmpl_reply', re.data);
            if(jq.trim(hotReplyHtml)!==''){
                jq('#hotLabelBox').show();
                jq('#hotReplyList').append(hotReplyHtml);
            }

            re.data.tmplType = 'all';
            var allReplyHtml = template('tmpl_reply', re.data);
            if(jq.trim(allReplyHtml)!==''){
                jq('#allLabelBox').show();
                jq('#allReplyList').css({height:'auto'})
                jq('#allReplyList').append(allReplyHtml);
            }
            jq('#loadNext').hide();
            exports.nextStart = re.data.nextStart;
        },

        init: function() {
            var tId = window.tId;

            //var action = jq.UTIL.getQuery('action');

            exports.load(exports.nextStart, 'drag');

            initLazyload('.warp img');

            // 主题和底部bar 帖点击回复
            jq('.warp, #bottomBar').on('click', '.threadReply', function() {
                var thisObj = jq(this),
                    callback = function() {
                        thread.reply(tId, null, '', 'comment');
                    };
                thread.checkIsRegistered(callback);
            });

            // 回复楼中楼
            jq('#hotReplyList,#allReplyList').on('click', '.replyFloor', function(e) {
                var thisObj = jq(this).parents('li');
                var authorUId = thisObj.attr('uId');
                // 获取帖子id
                var divId = thisObj.attr('id'), pId, floorPId, author;

                var callback = function() {
                    if (/p_[0-9a-f]{24}/.test(divId)) {
                        if (match = divId.match(/p_([0-9a-f]{24})/)) {
                            toPId = match[1];
                        }

                        e.stopPropagation();
                        jq.UTIL.touchStateNow(jq(this));

                        author = thisObj.attr('author');
                        thread.reply(tId, toPId, author, 'comment');
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

            // like
            jq('.topicCon .replyShare,#hotReplyList,#allReplyList').on('click', '.like', function(e) {
                jq.UTIL.touchStateNow(jq(this));
                e.stopPropagation();

                var thisObj = jq(this),
                    pId = thisObj.attr('pId') || null;

                var callback = function() {
                    if(thisObj.children('i').hasClass('iconPraise')) {
                        return;
                    }

                    var opts = {
                        'success': function(result) {
                            if (result.code == 0) {
                            //if (result.code == 0 && result.data && result.data.likeNum) {
                                jq.UTIL.likeTips(thisObj, '+1');
                                thisObj.html('<i class="iconPraise f18 cf"></i>' + (parseInt(thisObj.data('num')) + 1));
                            }
                        },
                        'noShowLoading' : true,
                        'noMsg' : true
                    }

                    var url = '/user/like/comments';
                    var data = {'tid':tId, 'coid': pId};

                    jq.UTIL.ajax(url, data, opts);
                };
                thread.checkIsRegistered(callback);
            });

            /**
             * @desc 全部回复加倒序查看
             * @param desc 为0是正序，为1时倒序
             */
            //var replySortBtn = jq('.evtReplySort'),
            //    replySortIcon = replySortBtn.find('i'),
            //    replySortSwitch = function () {
            //        if (!exports.desc) {
            //            replySortIcon.removeClass('iconSequence');
            //            replySortIcon.addClass('iconReverse');
            //            replySortBtn.html('倒序排列');
            //            replySortBtn.prepend(replySortIcon);
            //        } else {
            //            replySortIcon.removeClass('iconReverse');
            //            replySortIcon.addClass('iconSequence');
            //            replySortBtn.html('正序排列');
            //            replySortBtn.prepend(replySortIcon);
            //        }
            //    };
            //replySortSwitch();
            //replySortBtn.on('click', function () {
            //    var allReplyWrap = jq('#allReplyList'),
            //        allReplyHeight = allReplyWrap.height();
            //    allReplyWrap.css({height: allReplyHeight});
            //    allReplyWrap.html('');
            //    exports.nextStart = 0;
            //    exports.desc = !exports.desc ? 1 : 0;
            //    replySortSwitch();
            //    exports.load(exports.nextStart, 'sort');
            //    //pgvSendClick({hottag: 'wsq.reply.sort.inverse'});
            //});

        },

    };

    exports.init();

});
