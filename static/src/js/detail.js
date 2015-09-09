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
        isLoadingFirst: true,
        isLoading: false,
        isNoShowToTop: false,
        hasVoted: false,
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
            var url = '/topics/' + window.tId + '/proposals'
                + '?skip=' + start
                + '&desc=' + desc;

            if (exports.isLoadingFirst){
                url = '/topics/' + window.tId;
            }

            var opts = {
                'beforeSend': function() {
                    switch(action) {
                        //case 'pull':
                        //    jq('#refreshWait').show();
                        //    jq('#showAll').hide();
                        //    exports.isLoadingNew = true;
                        //    break;
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
                        if (exports.isLoadingFirst){
                            exports.render(re);
                        }
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
        render: function(re) {
            var topicHtml = template('tmpl_topic', re.data);
            jq('.detailBox').prepend(topicHtml);

            exports.isLoadingFirst = false;
            jq('.warp, #bottomBar, .recommendTitle').show();

            exports.hasVoted = re.data.has_voted || false;
        },

        renderList: function(re, clear) {
            if (clear) {
                jq('#allReplyList').html('');
            }

            // 最后无数据不再加载
            if (jq.UTIL.isObjectEmpty(re.data.dataList)) {
                exports.isLoadingNew = false;
                jq('#loadNext').hide();
                //jq('#showAll').show();
                if (clear) {
                    jq('#allLabelBox').show();
                    jq('.emptyList').html('还没有看法哦^…^').show()
                }
                return true;
            }
            //re.data.isWX = isWX;
            re.data.tmplType = 'default';
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

            //if (clear) {
            //    if (exports.order == 'hot') {
            //        jq('.badge').show();
            //    } else {
            //        jq('.badge').hide();
            //    }
            //}
        },

        init: function() {
            var tId = window.tId;
            var parentId = window.parentId || 0;

            // 分享遮罩，一次性
            //var action = jq.UTIL.getQuery('action');
            //var reapp = /qqdownloader\/([^\s]+)/i;

            exports.load(exports.nextStart, 'drag');

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
            //            jq('.g-mask').on('click', function() {
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

            // 主题和底部bar 帖点击回复
            jq('.warp, #bottomBar').on('click', '.threadReply', function() {
                var thisObj = jq(this),
                    callback = function() {
                    //thread.reply(tId, parentId, '', 'proposal');
                    thread.reply(tId, null, '', 'proposal');
                };
                jq.UTIL.touchStateNow(thisObj.parent('.topicTit'));
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

            jq('#hotReplyList,#allReplyList').on('click', '.proposalWrap', function(e) {
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
                    isFollowed = thisObj.hasClass('iconPraise');

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
                                thisObj.attr('class', 'item cf iconNoPraise');
                            }
                        };

                        jq.UTIL.ajax(url, data, opts, 'DELETE');
                    } else {
                        opts.success = function(result) {
                            if (result.code == 0) {
                                thisObj.attr('class', 'item cf iconPraise');
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

                                var url = '/user/unvote/proposals';
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

                        var url = '/user/vote/proposals';
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

                                var url = '/user/revote/proposals';
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
