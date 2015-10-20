
define(['uploadImg', 'art-template'], function(uploadImg, template) {

    template.helper('isDOMExist', function (id) {
        if (jq('#' + id)[0]) {
            return true;
        } else {
            return false;
        }
    });

    //template.helper('isObjEmpty', function (obj) {
    //    if (jq.isEmptyObject(obj)) {
    //        return true;
    //    } else {
    //        return false;
    //    }
    //});

    exports = {
        //popTId: 0,
        uploadTimer: null,
        isLoadingNew: true,
        isLoading: false,
        desc: 0,
        nextStart: 0,
        colorList: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#bcbd22', '#17becf', '#aec7e8'],

        // load data,all in one
        load: function(loadOpts, action) {

            exports.isLoading = true;

            var isList = loadOpts.isList || false,
                filterType = loadOpts.type || null,
                url = loadOpts.url,
                action = action || '',
                start = exports.nextStart;

            if (filterType) {
                url = url.indexOf('?') === -1 ? url + '?' : url + '&';
                url = url + 'type=' + filterType;
            }
            if (isList) {
                url = url.indexOf('?') === -1 ? url + '?' : url + '&';
                url = url + 'skip=' + start;
                //    + '&desc=' + desc;
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
                        case 'more':
                            jq.UTIL.showLoading();
                            break;
                        default:
                            jq.UTIL.showLoading();
                    }
                },
                'complete': function() {
                },
                'success': function(re) {
                    jq('#refreshWait').hide();
                    //jq('#loadNext').hide();
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
            opts.noMsg = true;
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
            if (jq.UTIL.isObjectEmpty(re.data.data_list)) {
                exports.isLoadingNew = false;
                jq('#loadNext').hide();
                jq('.loading').hide();
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
                opts.callback(re, clear);
            }
            if (re.data.next_start) {
                exports.nextStart = re.data.next_start;
            }
            jq('#loadNext').hide();
        },

        initShare: function(data) {
            var shareData = {
                title: data.title,
                desc: data.content,
                link: window.location.href,
                imgUrl: data.picture_urls.length > 0 ? data.picture_urls[0] : 'https://dn-geass-images.qbox.me/Fs0t-OATExfbYJO7EqWrVq1YmfbP',
            };

            wx.onMenuShareAppMessage(shareData);
            wx.onMenuShareTimeline(shareData);
            wx.onMenuShareQQ(shareData);
            wx.onMenuShareQZone(shareData);
            wx.onMenuShareWeibo(shareData);
        },

        initTouchRefresh: function (load) {

            //var level = /Android 4.0/.test(window.navigator.userAgent) ? -10 : -100;
            // 全屏触摸
            jq.UTIL.initTouch({
                obj: jq('.warp')[0],
                end: function(e, offset) {
                    document.ontouchmove = function(e){ return true;}
                    var loadingPos = jq('#loadNextPos');
                    //var loadingObj = jq('#loadNext');
                    // var loadingObjTop = loadingObj.offset().top + loadingObj.height() - jq(window).scrollTop();
                    //var loadingObjTop = loadingPos.offset().top - document.body.scrollTop - window.screen.availHeight;
                    var loadingObjTop = jq(document).height() - jq(window).scrollTop() - jq(window).height();
                    // 向上滑
                    if (offset.y > 0 && loadingObjTop <= 63 && exports.isLoadingNew && !exports.isLoading) {
                    //if (offset.y > 10 && loadingObjTop <= 10 && exports.isLoadingNew && !exports.isLoading) {
                        load('drag');
                        //exports.load(opts, 'drag');
                    }
                    // 向下拉刷新
                    //if (offset.y < level && document.body.scrollTop <= 0) {
                    //}
                }
            });

        },

        resetOpbar: function(thisObj, voteTotalNum, position, delayTime) {
            position = position || 0;
            delayTime = delayTime || 1;
            var opbar = thisObj.find('.opbar'),
                currNum = thisObj.children('.voteCount').data('num'),
                currPercent = voteTotalNum == 0 ? "0.00" : (parseInt(currNum)/voteTotalNum*100).toFixed(2);
                //currPercent = (parseInt(currNum)/voteTotalNum*100 + 1.0/(position+3)*100).toFixed(2);

            thisObj.children('.oppi').css("color",  exports.colorList[position % 10]).html(currPercent + '%');
            opbar.css("background-color", exports.colorList[position % 10]);
            if (parseInt(opbar.width()*100/opbar.offsetParent().width()) != parseInt(currPercent)) {
                opbar.delay(delayTime).animate({width: currPercent + '%'});
            }
        },

        resetAllOpbar: function() {
            var delayTime = 50,
                voteTotalNum = exports.voteTotalNum;
            jq('.opWrap').each(function(index){
                exports.resetOpbar(jq(this), voteTotalNum, index, delayTime);
                delayTime += 50;
            });
        },

        reply: function (url, toCoId, author, replyType) {
            var author = author || '',
                isLZ = window.isLZ || false,
                isAnonymBox = replyType == 'opinion' && !isLZ;

            // 未登录
            //if (authUrl) {
            //    jq.UTIL.reload(authUrl);
            //    return false;
            //}

            var replyDialog = function() {
                var replyTimer = null,
                    storageKey = replyType + '_content',
                    replyForm = template('tmpl_replyForm', {data:{
                    'toCoId':toCoId,
                    'isAnonymBox':isAnonymBox,
                }});

                if (!(toCoId && replyType == 'comment')) {
                    replyTimer = setInterval(function() {
                        if (jq('textarea[name="content"]').val()) {
                            localStorage.removeItem(storageKey);
                            localStorage.setItem(storageKey, jq('textarea[name="content"]').val());
                        }
                    }, 1000);
                }

                // 弹出回复框
                jq.UTIL.dialog({
                    content:replyForm,
                    id:'replyForm',
                    isHtml:true,
                    isMask:true,
                    top: 0,
                    // 弹出后执行
                    callback:function() {

                        var obj = {storageKey: storageKey, replyTimer: replyTimer, url: url, toCoId: toCoId, author: author, replyType: replyType};
                        exports.initReplyEvents(obj);

                    },
                    // 关闭回复框
                    close: function() {
                       // 内容非空确认
                       clearInterval(replyTimer);
                       //exports.isNoShowToTop = false;
                       //jq('.bNav').show();
                       //jq('.floatLayer').show();
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

        checkReplyForm: function(replyType) {
            var content = jq('textarea[name="content"]').val();
            var contentLen = jq.UTIL.mb_strlen(jq.UTIL.trim(content));

            if (replyType === 'opinion') {
                if (uploadImg.isBusy) {
                    jq.UTIL.dialog({content:'图片上传中，请稍候', autoClose:true});
                    return false;
                }

                if (contentLen <= 0) {
                    jq.UTIL.dialog({content:'看法不能为空', autoClose:true});
                    return false;
                }

                if (contentLen > 60000) {
                    jq.UTIL.dialog({content:'看法最好不要超过20000字哦', autoClose:true});
                    return false;
                }
            } else if (replyType === 'comment') {
                if (contentLen <= 0) {
                    jq.UTIL.dialog({content:'评论不能为空', autoClose:true});
                    return false;
                }

                if (contentLen > 2100) {
                    jq.UTIL.dialog({content:'评论不要超过700字哦', autoClose:true});
                    return false;
                }
            }

            return true;
        },

        initReplyEvents: function(obj){
            var storageKey = obj.storageKey;

            jq('#replyForm').attr('action', '/api/v1' + obj.url);

            if (obj.toCoId && obj.replyType == 'comment') {
                jq('textarea[name="content"]').attr('placeholder', '回复 ' + obj.author + '：');
            } else {
                // 信息恢复
                jq('textarea[name="content"]').val(localStorage.getItem(storageKey));
            }

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
                                if (!(obj.toCoId && obj.replyType == 'comment')) {
                                    localStorage.removeItem(storageKey);
                                }
                                var allLabelBox = jq('#allLabelBox'),
                                    //replyList = jq('#replyList'),
                                    replyData = {data_list:[re.data]};

                                jq('.emptyList').hide()

                                if (obj.replyType === 'opinion') {
                                    var listHtml = template('tmpl_opinions', replyData);
                                    if(jq.trim(listHtml)!==''){
                                        allLabelBox.show();
                                        jq('#allReplyList').append(listHtml);
                                    }

                                } else if (obj.replyType === 'proposal') {

                                    var listHtml = template('tmpl_proposals', replyData);
                                    if(jq.trim(listHtml)!==''){
                                        //jq('#hotLabelBox').show();
                                        jq('#hotReplyList').append(listHtml);
                                    }

                                } else if (obj.replyType === 'comment') {
                                    var listHtml = template('tmpl_reply', replyData);
                                    allLabelBox.show();
                                    //allLabelBox.next('.topicList').show();

                                    if (true && !exports.desc) {
                                        jq('#allReplyList').append(listHtml);
                                    } else {
                                        jq('#allReplyList').prepend(listHtml);
                                    }
                                }

                            }

                            clearInterval(obj.replyTimer);

                            // 关闭弹窗
                            //exports.isNoShowToTop = false;
                            jq.UTIL.dialog({id:'replyForm'});
                            //jq('.bNav').show();
                            //jq('.floatLayer').show();
                        }
                        isSendBtnClicked = false;
                    },
                    error:function(re) {
                        isSendBtnClicked = false;
                    }
                };
                if (!exports.checkReplyForm(obj.replyType)) {
                    return false;
                }
                isSendBtnClicked = true;
                jq.UTIL.ajaxForm('replyForm', opt, true);
                return false;
            });

            //exports.isNoShowToTop = true;
            // 隐藏底部导航和向上
            //jq('.bNav').hide();
            //jq('.floatLayer').hide();

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
                    'title':'前往微信授权？',
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
        //checkForm: function() {

        //    jq.each(uploadImg.uploadInfo, function(i,n) {
        //        if (n && !n.isDone) {
        //            jq.UTIL.dialog({content:'图片上传中，请等待', autoClose:true});
        //            return false;
        //        }
        //    });

        //    var content = jq('#content').val();
        //    var contentLen = jq.UTIL.mb_strlen(jq.UTIL.trim(content));
        //    if (contentLen < 15) {
        //        jq.UTIL.dialog({content:'内容过短', autoClose:true});
        //        return false;
        //    }

        //    return true;
        //},
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

                    var html = '<li id="li' + id + '"><div class="photoCut"><img src="https://dn-geass-static.qbox.me/static/img/defaultImg.png" class="attchImg" alt="photo"></div>' +
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

