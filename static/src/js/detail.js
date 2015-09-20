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
        hasVoted: false,
        isLoadingFirst: true,

        load: function(action) {
            var url = '/topics/' + window.tId,
                isLoadingFirst = exports.isLoadingFirst;

            thread.load({
                isList: !isLoadingFirst,
                isEmptyShow: true,
                url: isLoadingFirst ? url : url + '/opinions',
                emptyCon: '还没有看法哦！',
                callback: isLoadingFirst ? exports.render : exports.renderList,
            }, action);
        },

        // render data
        render: function(re) {
            var topicHtml = template('tmpl_topic', re.data);
                is_topic_followed = re.data.is_topic_followed || false;
            jq('.detailBox').prepend(topicHtml);

            var follow_class = is_topic_followed ? 'item cf iconFollow' : 'item cf iconNoFollow';
                follow_html = is_topic_followed ? '已关注' : '关注'
            jq('#bottomBar #follow').attr('class', follow_class).html(follow_html)

            jq('.warp, #bottomBar, .recommendTitle').show();

            window.isLZ = re.data.is_lz || false;
            exports.hasVoted = re.data.has_user_voted || false;
            exports.renderList(re);

            exports.isLoadingFirst = false;
        },

        renderList: function(re) {
            re.data.tmplType = 'default';
            var defaultReplyHtml = template('tmpl_reply', re.data);
            if(jq.trim(defaultReplyHtml)!==''){
                jq('#hotLabelBox').show();
                jq('#hotReplyList').append(defaultReplyHtml);
            }

            re.data.tmplType = 'all';
            var allReplyHtml = template('tmpl_reply', re.data);
            if(jq.trim(allReplyHtml)!==''){
                jq('#allLabelBox').show();
                jq('#allReplyList').css({height:'auto'})
                jq('#allReplyList').append(allReplyHtml);
            }
        },

        init: function() {
            var tId = window.tId;

            // 分享遮罩，一次性
            //var action = jq.UTIL.getQuery('action');
            //var reapp = /qqdownloader\/([^\s]+)/i;

            exports.load('drag');

            initLazyload('.warp img');

            // appbar no share mask
            //if (action == 'share' && !reapp.test(navigator.userAgent)) {
            //    var hadShowShareMask = localStorage.getItem('hadShowShareMask'),
            //        isMask = false;
            //    if (!hadShowShareMask) {
            //        isMask = true;
            //    }
            //    var tmpl = template.render('tmpl_pageTip', {'msg':'喜欢这个话题，请点击右上角图标分享'});
            //    jq.UTIL.dialog({
            //        id: 'shareMask',
            //        top:0,
            //        content: tmpl,
            //        isHtml: true,
            //        isMask: isMask,
            //        callback: function() {
            //            jq('.gMask').on('click', function() {
            //                jq.UTIL.dialog({id:'shareMask'});
            //            });
            //            jq('#showShare').on('click', function() {
            //                jq(this).hide();
            //            });
            //        }
            //    });
            //    localStorage.setItem('hadShowShareMask', 1);
            //}

            // 点击查看大图
            //require.async('module/imageviewCommon', function(imageviewCommon) {
            //    imageviewCommon.init('.slideShow li');
            //    imageviewCommon.init('.threadPic span');
            //    imageviewCommon.init('.replyImg dd');
            //    // imageviewCommon.init('.slideBox li');
            //});

            //setInterval(function() {
            //    if (window.pageYOffset > 1000 && !thread.isNoShowToTop) {
            //        jq('#goTop').show();
            //    } else {
            //        jq('#goTop').hide();
            //    }

            //}, 200);

            //jq('.upBtn').on('click', function() {
            //    jq('#goTop').hide();
            //    scroll(0,0);
            //});

            // 主题和底部bar 帖点击回复
            jq('.warp, #bottomBar').on('click', '.threadReply', function() {
                var thisObj = jq(this),
                    callback = function() {
                    thread.reply(tId, null, null, '', 'opinion');
                };
                jq.UTIL.touchStateNow(thisObj.parent('.topicTit'));
                thread.checkIsRegistered(callback);
            });

            thread.initTouchRefresh(exports.load);

            jq('#hotReplyList,#allReplyList').on('click', '.opinionWrap', function(e) {
                var thisObj = jq(this), link;
                jq.UTIL.touchStateNow(thisObj.parent('li'));

                link = thisObj.attr('data-link') || '';
                if (link) {
                    jq.UTIL.reload(link);
                }
                return false;
            });

            // follow
            jq('#bottomBar').on('click', '#follow', function(e) {

                jq.UTIL.touchStateNow(jq(this));
                e.stopPropagation();

                var thisObj = jq(this),
                    tId = window.tId || null,
                    isFollowed = thisObj.hasClass('iconFollow');

                var opts = {
                    'noShowLoading' : true,
                    'noMsg' : true
                };

                var url = '/user/following/topics',
                    data = {'tid':tId};

                var callback = function() {
                    if (isFollowed) {
                        opts.success = function(result) {
                            if (result.code == 0) {
                                thisObj.attr('class', 'item cf iconNoFollow');
                                thisObj.html('关注')
                            }
                        };

                        jq.UTIL.ajax(url, data, opts, 'DELETE');
                    } else {
                        opts.success = function(result) {
                            if (result.code == 0) {
                                thisObj.attr('class', 'item cf iconFollow');
                                thisObj.html('已关注')
                            }
                        };
                        jq.UTIL.ajax(url, data, opts);
                    }
                };
                thread.checkIsRegistered(callback);
            });

            // vote
            jq('#hotReplyList,#allReplyList').on('click', '.vote', function(e) {

                jq.UTIL.touchStateNow(jq(this));
                e.stopPropagation();

                var thisObj = jq(this),
                    pId = thisObj.attr('pId') || null,
                    isVoted = thisObj.hasClass('voted'),
                    voteNum = parseInt(thisObj.data('num'));

                var callback = function() {
                    if(isVoted && exports.hasVoted) {
                        var opts = {
                            'id':'operationConfirm',
                            'isMask':true,
                            'content':'可以取消这次投票重新选择，确定要取消吗',
                            'okValue':'确定',
                            'cancelValue':'取消',
                            'ok':function() {
                                var opts = {
                                    'success': function(result) {
                                        if (result.code == 0) {
                                            exports.hasVoted = false;
                                            jq.UTIL.likeTips(thisObj, '-1');
                                            thisObj.attr('class', 'voteCount vote');
                                            thisObj.html(voteNum - 1);
                                            thisObj.data('num', voteNum - 1);
                                        }
                                    },
                                    'noShowLoading' : true,
                                    'noMsg' : true
                                }

                                var url = '/user/unvote/opinions';
                                var data = {'tid':tId, 'pid': pId};

                                jq.UTIL.ajax(url, data, opts);
                            },
                        };
                        jq.UTIL.dialog(opts);
                    } else if (!isVoted && !exports.hasVoted){
                        var opts = {
                            'success': function(result) {
                                if (result.code == 0) {
                                    exports.hasVoted = true;
                                    jq.UTIL.likeTips(thisObj, '+1');
                                    thisObj.attr('class', 'voteCount voted vote');
                                    thisObj.html(voteNum + 1);
                                    thisObj.data('num', voteNum + 1)
                                }
                            },
                            'noShowLoading' : true,
                            'noMsg' : true
                        }

                        var url = '/user/vote/opinions';
                        var data = {'tid':tId, 'pid': pId};

                        jq.UTIL.ajax(url, data, opts);
                    } else if (!isVoted && exports.hasVoted) {
                        var opts = {
                            'id':'operationConfirm',
                            'isMask':true,
                            'content':'要取消之前的投票重新选择吗?',
                            'okValue':'确定',
                            'cancelValue':'取消',
                            'ok':function() {
                                var opts = {
                                    'success': function(result) {
                                        if (result.code == 0) {
                                            var votedObj = jq('.voted');
                                            oldVoteNum = parseInt(votedObj.data('num'));
                                            votedObj.attr('class', 'voteCount vote');
                                            votedObj.html(oldVoteNum - 1);
                                            votedObj.data('num', oldVoteNum - 1);

                                            jq.UTIL.likeTips(thisObj, '+1');
                                            thisObj.attr('class', 'voteCount voted vote');
                                            thisObj.html(voteNum + 1);
                                            thisObj.data('num', voteNum + 1)
                                        }
                                    },
                                    'noShowLoading' : true,
                                    'noMsg' : true
                                }

                                var url = '/user/revote/opinions';
                                var data = {'tid':tId, 'pid': pId};

                                jq.UTIL.ajax(url, data, opts);
                            },
                        };
                        jq.UTIL.dialog(opts);

                    }
                };
                thread.checkIsRegistered(callback);
            });

        },

    };

    exports.init();

});
