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

            // 默认展开回复
            //if (action == 'reply') {
            //    thread.reply(sId, tId, parentId, 0, 0, '', true);
            //}

            // 头部点击
            //jq('.detail').on('click', function() {
            //    if (sId && parentId != 0) {
            //        jq.UTIL.open('/' + sId + '/v/' + parentId);
            //        return false;
            //    }
            //    if (sId) {
            //        jq.UTIL.open('/' + sId);
            //        return false;
            //    }
            //});

            // 图片横滑
            //exports.initShowPic(parentId);

            // 点击查看大图
            //require.async('module/imageviewCommon', function(imageviewCommon) {
            //    imageviewCommon.init('.slideShow li');
            //    imageviewCommon.init('.threadPic span');
            //    imageviewCommon.init('.replyImg dd');
            //    // imageviewCommon.init('.slideBox li');
            //});

            //jq.UTIL.touchState('#support');

            // 回复内容点击
            jq('.warp').on('click', '.replyUser, .replyShare, .replyPop, .replyPop .replyFloor', function(e) {
                var obj = jq(this);
                jq.UTIL.touchStateNow(obj);

                var divId = obj.parents('li').attr('id'), pId, floorPId;
                var authorUId = obj.parents('li').attr('uId');
                var author = obj.parents('li').attr('author');

                //if (isManager || authorUId == uId) {
                //    if (divId) {
                //        if (match = divId.match(/p_(\d+)_(\d+)_(\d+)/)) {
                //            pId = match[2];
                //            floorPId = match[3];
                //        }
                //    }

                //    if (isManager) {
                //        thread.showManagerPanel(tId, parentId, pId, floorPId, authorUId, author, true, true);
                //        return false;
                //    }

                //    if (authorUId == uId) {
                //        thread._delReply(tId, pId, floorPId, true);
                //        return false;
                //    }

                //}
            });

            // 主题和底部bar 帖点击回复
            //jq.UTIL.touchState('.threadReply', 'commBg', '.warp');
            //jq.UTIL.touchState('.threadReply', 'commBg', '#bottomBar');
            jq('.warp, #bottomBar').on('click', '.threadReply', function() {
                var thisObj = jq(this),
                    callback = function() {
                    //thread.reply(tId, parentId, '', 'proposal');
                    thread.reply(tId, null, '', 'proposal');
                };
                jq.UTIL.touchStateNow(thisObj.parent('.topicTit'));
                thread.checkIsRegistered(callback);
            });

            //点击视频播放
            //jq('.warp').on('click', '.videoPlay', function() {
            //    var thisObjUrl = jq(this).attr('data-url') || '';
            //    var thisObjVid = jq(this).attr('data-vid') || '';
            //    var parent = jq(this).parent();
            //    var width = parent.find('img').width();
            //    var height = parent.find('img').height();
            //    parent.html('<video width="'+width+'" height="'+height+'" class="video" autoplay="autoplay" src="'+thisObjUrl+'" controls="controls"></video>')
            //});
            //列表点击播放进入详情页
            //if(jq.UTIL.getQuery('video')) {
            //    jq("html,body").animate({scrollTop:jq('#videoBox').offset().top - 50},1000);
            //    jq('.videoPlay').click();
            //}


            //* 回复楼中楼
            //jq('#hotReplyList,#allReplyList').on('click', '.replyFloor', function(e) {
            //    var thisObj = jq(this).parents('li');
            //    var authorUId = thisObj.attr('uId');
            //    // 获取帖子id
            //    var divId = thisObj.attr('id'), pId, floorPId, author;
            //    if (/p_\d+_\d+_\d+/.test(divId)) {
            //        if (match = divId.match(/p_(\d+)_(\d+)_(\d+)/)) {
            //            pId = match[2];
            //            floorPId = match[3];
            //        }
            //        // console.log(floorPId);
            //        // 管理员点击楼中楼，进入管理流程
            //        if ((isManager || authorUId == uId) && floorPId > 0) {
            //            return;
            //        }

            //        e.stopPropagation();
            //        jq.UTIL.touchStateNow(jq(this));

            //        author = thisObj.attr('author');
            //        thread.reply(tId, parentId, pId, floorPId, author, true);
            //    }
            //});

            // 点击查看更多楼中楼
            //jq('#hotReplyList,#allReplyList').on('click', '.moreInReply', function(e) {
            //});

            // exports.picTId = window.picThreadTId;
            exports.nextStart = window.nextStart;

            // 翻页相关
            var query = '';
            if (window.location.search.indexOf('?') !== -1) {
                query = window.location.search.replace(/\?/g, '&');
            }
            // 消息页过来查看楼中楼 禁用上滑
            var getFloorPId = jq.UTIL.getQuery('floorPId') || 0;
            var getPId = jq.UTIL.getQuery('pId') || 0;
            if (getFloorPId || getPId) {
                exports.isLoadingNew = false;
                jq('#showAllReply').on('click', function() {
                    var url = window.location.href.replace(/&?pId=\d+/, '');
                    jq.UTIL.reload(url);
                }).show();
                jq('#showAll').hide();
            }

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
                jq.UTIL.touchStateNow(jq(this).parent('li'));
                jq.UTIL.reload(jq(this).data('link'));
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
            /**
             * @desc 全部回复加倒序查看
             * @param desc 为0是正序，为1时倒序
             */
            var replySortBtn = jq('.evtReplySort'),
                replySortIcon = replySortBtn.find('i'),
                replySortSwitch = function () {
                    if (!exports.desc) {
                        replySortIcon.removeClass('iconSequence');
                        replySortIcon.addClass('iconReverse');
                        replySortBtn.html('倒序排列');
                        replySortBtn.prepend(replySortIcon);
                    } else {
                        replySortIcon.removeClass('iconReverse');
                        replySortIcon.addClass('iconSequence');
                        replySortBtn.html('正序排列');
                        replySortBtn.prepend(replySortIcon);
                    }
                };
            replySortSwitch();
            replySortBtn.on('click', function () {
                var allReplyWrap = jq('#allReplyList'),
                    allReplyHeight = allReplyWrap.height();
                allReplyWrap.css({height: allReplyHeight});
                allReplyWrap.html('');
                exports.nextStart = 0;
                exports.desc = !exports.desc ? 1 : 0;
                replySortSwitch();
                exports.load(exports.nextStart, 'sort');
                //pgvSendClick({hottag: 'wsq.reply.sort.inverse'});
            });

            /**
             * @desc 相关话题推荐
             */
            jq('.warp').on('click', '.evtTopicCon',function () {
                var link = jq(this).attr('data-link') || '';
                if (link) {
                    jq.UTIL.open(link + '?ADTAG=wsq.xiangqing.tuijian.click');
                    return false;
                }
            }).on('click', '.evtAuthorUrl',function (e) {
                e.stopPropagation(e);
                var link = jq(this).attr('data-link') || '';
                if (link) {
                    jq.UTIL.open(link);
                }
                return false;
            }).on('click', '.evtMoreHot', function (e) {
                e.stopPropagation(e);
                var link = jq(this).attr('data-link') || '';
                if (link) {
                    jq.UTIL.open(link + '&ADTAG=wsq.remenbiaoqian.tuijian.click');
                }
                return false;
            });

            // 话题推荐
            //exports.recommendThread();
            // 全局活动
            //thread.publicEvent();
            // 管理
            //thread.initPopBtn();
        },

    };

    exports.init();

    //jq.UTIL.dialog({content:navigator.userAgent.toLowerCase(),autoClose:true});

});
