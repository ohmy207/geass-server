
define(['uploadImg', 'art-template'], function(uploadImg, template) {

    template.helper('isDOMExist', function (id) {
        if (jq('#' + id)[0]) {
            return true;
        } else {
            return false;
        }
    });

    template.helper('getWinParams', function (name) {
        return window[name];
    });

    template.helper('isObjEmpty', function (obj) {
        if (jq.isEmptyObject(obj)) {
            return true;
        } else {
            return false;
        }
    });

    exports = {
        //popTId: 0,
        uploadTimer: null,
        isLoadingNew: true,
        isLoading: false,
        desc: 0,
        nextStart: 0,

        // load data,all in one
        load: function(loadOpts, action) {

            action = loadOpts.action || '';
            exports.isLoading = true;

            var isList = loadOpts.isList || false,
                url = loadOpts.url,
                start = exports.nextStart,
                desc = exports.desc;

            if (isList) {
                url = loadOpts.url + '?skip=' + start,
                    + '&desc=' + desc;
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
                        //var zero = new Date;
                        exports.render(re, loadOpts, !start);
                        //stat.reportPoint('listRender', 10, new Date, zero);
                    } else {
                        jq.UTIL.dialog({content: '获取数据失败，请重试', autoClose: true});
                    }
                    exports.isLoading = false;
                }
            };
            jq.UTIL.ajax(url, '', opts);
        },

        // render data
        render: function(re, opts, clear) {
            //if (clear) {
            //    jq('#allReplyList').html('');
            //}

            var isList = opts.isList || false,
                isEmptyShow = opts.isEmptyShow || false,
                emptyCon = opts.emptyCon || '';

            // 最后无数据不再加载
            if (jq.UTIL.isObjectEmpty(re.data.dataList)) {
                exports.isLoadingNew = false;
                jq('#loadNext').hide();
                //jq('#showAll').show();
                if (clear && isEmptyShow) {
                    jq('#allLabelBox').show();
                    jq('.emptyList').html(emptyCon).show()
                }
                if (isList) {
                    return true;
                }
            }

            if (typeof opts.callback == 'function') {
                opts.callback(re);
            }

            jq('#loadNext').hide();
            exports.nextStart = re.data.nextStart;
        },

        initTouchRefresh: function (load) {

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
                        load('drag');
                        //exports.load(opts, 'drag');
                    }
                    // 向下拉刷新
                    if (offset.y < level && document.body.scrollTop <= 0) {
                    }
                }
            });

        },

        reply: function (tId, toPId, author, replyType) {
            //var isViewthread = isViewthread || false;
            var author = author || '';
            //var floorPId = floorPId || 0;
            //var nodeId = nodeId || 't_' + tId  + '_0_0';

            // 未登录
            //if (authUrl) {
            //    jq.UTIL.reload(authUrl);
            //    return false;
            //}

            var replyDialog = function() {
                var replyTimer = null;
                var replyForm = template('tmpl_replyForm', {data:{'tId':tId, 'toPId':toPId}});

                // 弹出回复框
                jq.UTIL.dialog({
                    content:replyForm,
                    id:'replyForm',
                    isHtml:true,
                    isMask:true,
                    top: 0,
                    // 弹出后执行
                    callback:function() {

                        //非回复主帖，隐藏发图
                        //if(!hasTid){jq('.uploadPicBox').css('visibility', 'hidden')};

                        var obj = {replyTimer: replyTimer, toPId: toPId, author: author, tId: tId, replyType: replyType};
                        //初始化回复窗口事件
                        exports.initReplyEvents(obj);

                    },
                    // 关闭回复框
                    close: function() {
                       // 内容非空确认
                       clearInterval(replyTimer);
                       exports.isNoShowToTop = false;
                       jq('.bNav').show();
                       jq('.floatLayer').show();
                       return true;

                       // 文本框焦点
                       jq('#replyForm .sInput').blur();
                   }
                });
            }

            //不加入社区也可发帖，自动加入社区修改
            replyDialog();

            return true;
        },

        checkReplyForm: function() {
            var content = jq('textarea[name="content"]').val();
            var contentLen = jq.UTIL.mb_strlen(jq.UTIL.trim(content));
            if (contentLen <= 0) {
                jq.UTIL.dialog({content:'回复内容不能为空', autoClose:true});
                return false;
            }

            return true;
        },
        //初始化回复窗口事件
        initReplyEvents: function(obj){
            //var storageKey = obj.sId + 'reply_content';
            //require.async('module/emotion', function(emotion) {
            //    // 表情开关
            //    var reInit = true;
            //    emotion.init(reInit);

            //    //此种写法兼容ios7
            //    //jq('.iconExpression').on('touchstart', emotion.toggle);
            //    //jq('.iconExpression').on('click', emotion.toggle);

            //    //表情 图片点击切换
            //    var aOperatIcon = jq('.operatIcon');
            //    aOperatIcon.on('click', function(){
            //        var thisObj = jq(this);
            //        var thisNum = thisObj.attr('data-id');
            //        var aOperatList = jq('.operatList');
            //        aOperatList.hide();
            //        jq(aOperatList[thisNum]).show();
            //        if(thisNum == 0){
            //            jq('.expreList').show();
            //            jq('.expreBox').show();
            //        }
            //        //如果是当前选中状态，则点击隐藏
            //        if(thisObj.hasClass('on')){
            //            jq(aOperatList[thisNum]).hide();
            //            thisObj.removeClass('on');
            //        }else{
            //            aOperatIcon.removeClass('on');
            //            thisObj.addClass('on');
            //        }
            //    });
            //    //表情总个数大于手机宽度时显示更多按钮
            //    var expressionMenu = jq('.expressionMenu').find('a');
            //    var haveMenuWidth = expressionMenu.length*76;
            //    var operatingBoxWidth = jq('.operatingBox').width();
            //    if(haveMenuWidth > operatingBoxWidth){
            //        jq('.iconArrowR').show();
            //    };
            //    //输入框选中时隐藏表情，如果当只有表情打开时
            //    /*jq('#content').on('focus', function(){
            //        if(jq('.photoTipsBox').is(':hidden')){
            //            emotion.hide();
            //            aOperatIcon.removeClass('on');
            //        }
            //    });*/

            //});

            if (obj.replyType === 'opinion') {
                jq('#replyForm').attr('action','/api/v1/topics/'+obj.tId+'/opinions');
            }
            else if (obj.replyType === 'comment') {
                jq('#replyForm').attr('action','/api/v1/topics/'+obj.tId+'/comments');

                if (obj.toPId) {
                    jq('textarea[name="content"]').attr('placeholder', '回复 ' + obj.author + '：');
                }
            }

            //if (obj.pId > 0) {
            //    //jq('#replyForm').attr('action', '/' + obj.sId + '/f/new/submit');
            //    jq('#replyForm').attr('action', '/c/new/submit');
            //    jq('textarea[name="content"]').attr('placeholder', '回复 ' + obj.author + '：');
            //    jq('input[name="floorPId"]').val(obj.floorPId);
            //} else {
            //    //jq('#replyForm').attr('action', '/' + obj.sId + '/r/new/submit');
            //    jq('#replyForm').attr('action', '/r/new/submit');
            //    // 信息恢复
            //    //jq('textarea[name="content"]').val(localStorage.getItem(storageKey));
            //}

            // 发送按纽绑定
            var isSendBtnClicked = false;
            jq('#comBtn').on('click', function() {
                if (isSendBtnClicked){
                    return false;
                }
                var opt = {
                    success:function(re) {
                        var status = parseInt(re.code);
                        if (status === 0) {
                            if (re.data.author_uid) {
                                //localStorage.removeItem(storageKey);
                                // 回复回复
                                //if (obj.parentId) {
                                //    var tmpl = template('tmpl_reply_floor', {floorList:{0:re.data}});
                                //    jq('#fl_' + obj.parentId + ' ul').append(tmpl);
                                //    jq('#fl_' + obj.parentId).parent().parent().show();
                                //    // 普通回复
                                //} else {
                                    // 直接显示回复的内容到页面
                                    // 格式化用户等级
                                    //if(re.data.authorExpsRank){
                                    //    re.data.authorExps = {};
                                    //    re.data.authorExps.rank = re.data.authorExpsRank;
                                    //}
                                    //re.data.restCount = 0;
                                    //var tmpl = template('tmpl_reply', {replyList:{0:re.data}, rIsAdmin:window.isManager, rGId:window.gId, groupStar:window.groupStar, isWX:window.isWX});
                                // 结构变了与列表不同
                                var allLabelBox = jq('#allLabelBox'),
                                    //replyList = jq('#replyList'),
                                    replyData = {replyList:{0:re.data}};

                                if (obj.replyType === 'opinion') {
                                    replyData.tmplType = 'all';
                                    var allReplyHtml = template('tmpl_reply', replyData);
                                    if(jq.trim(allReplyHtml)!==''){
                                        allLabelBox.show();
                                        jq('#allReplyList').append(allReplyHtml);
                                    }

                                    replyData.tmplType = 'default';
                                    var defaultReplyHtml = template('tmpl_reply', replyData);
                                    if(jq.trim(defaultReplyHtml)!==''){
                                        jq('#hotLabelBox').show();
                                        jq('#hotReplyList').append(defaultReplyHtml);
                                    }

                                } else if (obj.replyType === 'comment') {
                                    var tmpl = template('tmpl_reply', replyData);
                                    allLabelBox.show();
                                    //allLabelBox.next('.topicList').show();

                                    if (!window.desc) {
                                        jq('#allReplyList').append(tmpl);
                                    } else {
                                        jq('#allReplyList').prepend(tmpl);
                                    }
                                }
                                    /**
                                     * @desc    window.desc from viewthread.js, 回复列表排序 0 或者 1, 默认 0
                                     *          如果为1，发表的新内容插入到列表最上面，否则插入到列表最下面
                                     */

                                    //jq('#rCount').html(re.data.rCount);
                                    //replyList.parent().show();
                                //}
                            }
                            // initLazyload('.warp img');

                            clearInterval(obj.replyTimer);

                            // 关闭弹窗
                            exports.isNoShowToTop = false;
                            jq.UTIL.dialog({id:'replyForm'});
                            jq('.bNav').show();
                            jq('.floatLayer').show();
                        }
                        isSendBtnClicked = false;
                    },
                    error:function(re) {
                        isSendBtnClicked = false;
                    }
                };
                if (!exports.checkReplyForm()) {
                    return false;
                }
                isSendBtnClicked = true;
                jq.UTIL.ajaxForm('replyForm', opt, true);
                return false;
            });

            // 输入框文字计算
            obj.replyTimer = setInterval(function() {
                //jq.UTIL.strLenCalc(jq('textarea[name="content"]')[0], 'pText', 280);
                if (jq('textarea[name="content"]').val()) {
                    //localStorage.removeItem(storageKey);
                    //localStorage.setItem(storageKey, jq('textarea[name="content"]').val());
                }
            }, 1000);

            exports.isNoShowToTop = true;
            // 隐藏底部导航和向上
            jq('.bNav').hide();
            jq('.floatLayer').hide();

            jq('#fwin_dialog_replyForm').css('top', '0');

            jq('#cBtn').bind('touchstart', function() {
                jq(this).addClass('cancelOn');
            }).bind('touchend', function() {
                jq(this).removeClass('cancelOn');
                if(jq.os.android && parseInt(jq.os.version) <= 2){
                    jq(this).click();
                }
            });

            jq('#comBtn').bind('touchstart', function() {
                jq(this).addClass('sendOn');
            }).bind('touchend', function() {
                jq(this).removeClass('sendOn');
            });

            exports.initUpload();

        },
        checkIsRegistered: function(callback) {
            if (!window.isRegistered) {
                var opts = {
                    'id':'operationConfirm',
                    'isMask':true,
                    'content':'本操作需要获取用户昵称及头像信息，要继续吗？',
                    'okValue':'确定',
                    'cancelValue':'取消',
                    'ok':function() {
                        jq.UTIL.reload(window.registerURL)
                    },
                };
                jq.UTIL.dialog(opts);
            } else {
                callback();
            }
        },
        checkForm: function() {

            jq.each(uploadImg.uploadInfo, function(i,n) {
                if (n && !n.isDone) {
                    jq.UTIL.dialog({content:'图片上传中，请等待', autoClose:true});
                    return false;
                }
            });

            var content = jq('#content').val();
            var contentLen = jq.UTIL.mb_strlen(jq.UTIL.trim(content));
            if (contentLen < 15) {
                jq.UTIL.dialog({content:'内容过短', autoClose:true});
                return false;
            }

            return true;
        },
        initUpload: function() {
            // 上传图片的绑定
            jq('#addPic, .uploadPicBox').on('click', function() {
                if(!uploadImg.checkUploadBySysVer()){
                    return false;
                };
            });

            jq('#uploadFile, #fistUploadFile').on('click', function() {
                var thisObj = jq(this);
                if (uploadImg.isBusy) {
                    jq.UTIL.dialog({content:'上传中，请稍后添加', autoClose:true});
                    return false;
                }
            });

            jq('body').on('click', '.iconSendImg, .iconArrowR', function(e){
                var thisObj = jq(this);
                var photoList = jq('.photoList');
                //点击图片图标
                if(thisObj.hasClass('iconSendImg')){
                    if(photoList.is(':hidden')){
                        photoList.show();
                    }
                }
                //查看更多表情
                if(thisObj.hasClass('iconArrowR')){
                    var expressionMenu = jq('.expressionMenu').find('a');
                    var haveMenuWidth = expressionMenu.length*76;
                    var expressionTabWidth = jq('.expressionTab').width();
                    if(haveMenuWidth > expressionTabWidth){
                        var firstChild = jq(expressionMenu[0]);
                        jq('.expressionMenu').append(firstChild.clone());
                        firstChild.remove();
                    }else{
                        jq.UTIL.dialog({id:'haveMoreExpression', content:'没有更多表情了哦~',autoClose:true});
                    }
                }

            });
            //首次点击图片的图标，触发一次手机的默认上传事件
            jq('body').on('change', '#fistUploadFile', function(e){
                var content = jq('#content')[0];
                jq('.photoList').show();
                jq('.operatList').hide();
                jq('.photoTipsBox').show();
                jq('.operatIcon').removeClass('on');
                jq('.iconSendImg').addClass('on');

                //传图时输入框定位到底部
                content.scrollTop = content.scrollHeight
            });

            // 文件表单发生变化时
            jq('body').on('change', '#uploadFile, #fistUploadFile', function(e) {
                //执行图片预览、压缩定时器
                uploadTimer = setInterval(function() {
                    // 预览
                    setTimeout(function() {
                        if (uploadImg.previewQueue.length) {
                            var jobId = uploadImg.previewQueue.shift();
                            uploadImg.uploadPreview(jobId);
                        }
                    }, 1);
                    // 上传
                    setTimeout(function() {
                        if (!uploadImg.isBusy && uploadImg.uploadQueue.length) {
                            var jobId = uploadImg.uploadQueue.shift();
                            uploadImg.isBusy = true;
                            uploadImg.createUpload(jobId, 'replyForm', uploadTimer);
                        }
                    }, 10);
                }, 300);

                e = e || window.event;
                var fileList = e.target.files;
                uploadNum = jq('.photoList').find('li').length || 0;
                if (!fileList.length) {
                    return false;
                }

                for (var i = 0; i<fileList.length; i++) {
                    if (uploadNum > 8) {
                        jq.UTIL.dialog({content:'你最多只能上传8张照片',autoClose:true});
                        break;
                    }

                    var file = fileList[i];

                    if (!uploadImg.checkPicType(file)) {
                        jq.UTIL.dialog({content: '上传照片格式不支持',autoClose:true});
                        continue;
                    }
                    if (!uploadImg.checkPicSize(file)) {
                        jq.UTIL.dialog({content: '图片体积过大', autoClose:true});
                        continue;
                    }

                    var id = Date.now() + i;
                    // 增加到上传对象中, 上传完成后，修改为 true
                    uploadImg.uploadInfo[id] = {
                        file: file,
                        isDone: false,
                    };

                    var html = '<li id="li' + id + '"><div class="photoCut"><img src="http://dzqun.gtimg.cn/quan/images/defaultImg.png" class="attchImg" alt="photo"></div>' +
                            '<div class="maskLay"></div>' +
                            '<a href="javascript:;" class="cBtn cBtnOn pa db" title="" _id="'+id+'">关闭</a></li>';
                    jq('#addPic').before(html);

                    uploadImg.previewQueue.push(id);

                    // 图片已经上传了 8 张，隐藏 + 号
                    if (uploadNum > 7) {
                        jq('#addPic').hide();
                    }

                    //更新剩余上传数
                    setTimeout(function(){
                        uploadImg.uploadRemaining();
                    }, 400);

                }
                // 把输入框清空
                jq(this).val('');

            });

            jq('.photoList').on('click', '.cBtn', function() {

                var id = jq(this).attr('_id');
                // 取消这个请求
                if (uploadImg.xhr[id]) {
                    uploadImg.xhr[id].abort();
                }
                // 图片删除
                jq('#li' + id).remove();
                // 表单中删除
                jq('#input' + id).remove();
                delete uploadImg.uploadInfo[id];

                // 图片变少了，显示+号
                if (uploadImg.countUpload() < uploadImg.maxUpload) {
                    jq('#addPic').show();
                    jq('.iconSendImg').removeClass('fail');
                }
                //更新剩余上传数
                uploadImg.uploadRemaining();

            });

        }
    };

    return exports
});

