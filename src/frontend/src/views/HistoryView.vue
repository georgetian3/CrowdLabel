<template>
  <div class="all">
    <div class="top_nav">
      <div class="top_nav_trigger">
        <img src="../assets/label.png" alt="label" height="26">
        <h2 class="logo">CrowdLabel</h2>
      </div>
      <div class="page_title">
        <h3 class="title">历史记录</h3>
        <a class="my_account" data-external="true" href="/myaccount">
            <img :src="profile_pic" class="profile" alt="label"/>
        </a>
      </div>
    </div>
    <div class="body">
        <div class="left_nav">
            <ul class="left_nav_list_top">
                <li>
                    <a aria-current="page" class="left_nav_list_item" data-external="true" href="/projects">
                        <img src="../assets/folder.png" height="21" width="20">
                        <p class="list_item_title">任务大厅</p>
                    </a>
                </li>
                <li>
                    <a aria-current="page" class="left_nav_list_item left_nav_list_item_active" data-external="true" href="/history">
                        <img src="../assets/history_active.png" height="19" width="20">
                        <p class="list_item_title">历史记录</p>
                    </a>
                </li>
                <li>
                    <a aria-current="page" class="left_nav_list_item" data-external="true" href="/credits">
                        <img src="../assets/credits.png" height="19" width="20">
                        <p class="list_item_title">我的积分</p>
                    </a>
                </li>
                <li>
                    <a aria-current="page" class="left_nav_list_item" data-external="true" href="/draftbox">
                        <img src="../assets/draftbox.png" height="21" width="21">
                        <p class="list_item_title">草稿箱</p>
                    </a>
                </li>
                <li tag="li" class="left_nav_spacer">
                </li>
            </ul>
            <ul class="left_nav_list_bottom">
                <li>
                    <a aria-current="page" class="left_nav_list_item" data-external="true" href="/myaccount">
                        <img src="../assets/settings.png" height="20" width="20">
                        <p class="list_item_title">设置</p>
                    </a>
                </li>
                <li>
                    <a aria-current="page" class="left_nav_list_item" data-external="true" href="https://github.com/crowdlabel">
                        <img src="../assets/about.png" height="20" width="20">
                        <p class="list_item_title">关于我们</p>
                    </a>
                </li>
            </ul>
        </div>
        <div class="main_body">
          <div class="filter">
              <p class="title_filter">筛选：</p>
              <div>
              <el-radio-group v-model="taskType" size="small" @change="chooseType()">
                <el-radio-button label="all">全部</el-radio-button>
                <el-radio-button label="text" >文字分类</el-radio-button>
                <el-radio-button label="img_classify" >图片分类</el-radio-button>
                <el-radio-button label="img_borderbox" >图片打标</el-radio-button>
                <el-radio-button label="audio">音频分类</el-radio-button>
              </el-radio-group>
              </div>
          </div>
            <div class="scroll_view">
              <el-scrollbar style="height: 100%">
                <!-- 如果没有任务 -->
                <div class="message" id="is_empty">
                  <p class="message_text">这里空空如也，快去接收任务吧！</p>
                </div>
                <!-- 用于展示下拉，填充的内容 -->
                <div class="scroll_element" v-for="(item, index) in projectsList" :key="index" @click="seeDetails(item.task_id)">
                  <img :src=item.cover class="project_image">
                  <div class="scroll_element_text">
                    <h4 class="project_title">{{ item.name }}</h4>
                    <p class="project_detail">任务类型: {{ item.type }}</p>
                    <p class="project_detail">任务标签: {{ item.tags }}</p>
                    <p class="project_detail">任务状态: 已完成 </p>
                    <p class="project_detail">获得积分: {{ item.credits }} </p>
                  </div>
                </div>
              </el-scrollbar>
            </div>
        </div>
    </div>
  </div>
</template>


<script>
// @ is an alias to /src
// import HelloWorld from '@/components/HelloWorld.vue'
import { ApiClient } from '@/crowdlabel-api/src';
import { UsersApi } from '@/crowdlabel-api/src';
import { AuthApi } from '@/crowdlabel-api/src';
import { TasksApi } from '@/crowdlabel-api/src';
export default {
  data() {
    return {
      taskType: 'all',
      client:'',
      user:'',
      task:'',
      auth:'',
      projectsList: [],
      profile_pic:''
    };
  },
  mounted() {
    let self = this;
    let base = this.$root.basePath
    var apiClient  = new ApiClient(base);
    apiClient.authentications['OAuth2PasswordBearer'].accessToken = localStorage.getItem('Authorization')
    self.client = apiClient
    var usersApi = new UsersApi(apiClient);
    self.user = usersApi
    var authApi = new AuthApi(apiClient);
    this.auth = authApi
    var tasksApi = new TasksApi(apiClient);
    self.task = tasksApi;
    self.user.getMeUsersMeGet((error, data, response) => {
      if (error == 'Error: Unauthorized') {
        localStorage.removeItem('Authorization');
        this.$router.push('/receiverlogin');
      }
      let res = JSON.parse(response["text"]);
      let tasks_completed = res["tasks_completed"];
      console.log(tasks_completed)
      if (tasks_completed.length > 0)
        document.getElementById("is_empty").remove();
      for (let i = 0; i < tasks_completed.length; i++) {
        let _task_id = tasks_completed[i];
        self.task.getTaskTasksTaskIdGet(_task_id, (error, data, response) => {
          let res = response.body;
            self.task.getCoverTasksTaskIdCoverImageGet(res.task_id, (error, data, response) => {
              // 任务信息
              let _name = res.name;
              let _tags = '';
              let _type = '';
              let _credits = res.credits;
              let task_tags = res.tags;
              for (var k = 0; k < task_tags.length; k++) {
                _tags += task_tags[k];
                if (k != task_tags.length - 1) {
                  _tags += ", ";
                }
                if (task_tags[k] == "文字分类" || task_tags[k] == "图片分类" || task_tags[k] == "图片打标" || task_tags[k] == "音频分类")
                  _type = task_tags[k];
              }
              // 任务封面
              let _cover = '';
              if (response.status == 400){
                _cover = '../default_cover.jpeg'
              } else {
                let binaryData = [];
                binaryData.push(response.body);
                let imageObjectURL = window.URL.createObjectURL(new Blob(binaryData));
                _cover = imageObjectURL;
              }
              let cur_task = {task_id: _task_id, name: _name, type: _type, tags: _tags, credits: _credits, cover: _cover};
              self.projectsList.push(cur_task);
            });
          });
      }
    })
    self.user.getPfpUsersMeProfilePictureGet((error, data, response) => {
      if (response.status == 404){
        self.profile_pic = '../my_account.svg'
      } else {
        let binaryData = [];
        binaryData.push(response.body);
        let imageObjectURL = window.URL.createObjectURL(new Blob(binaryData));
        self.profile_pic = imageObjectURL
      }
    })
  },
  methods: {
    seeDetails(task_id) {
      console.log("CLICKED")
      this.$store.commit('changeTaskID', task_id);
      this.$router.push({
        name:'project_detail',
      })
    },
    chooseType() {
      let self = this
      self.projectsList = []
      var taglist = []
      if(self.taskType=='text'){
        taglist.push("文字分类")
      }else if(self.taskType=='img_classify'){
        taglist.push("图片分类")
      }else if(self.taskType=='img_borderbox'){
        taglist.push("图片打标")
      }else if(self.taskType=='audio'){
        taglist.push("音频分类")
      }
      self.task.searchTasksTasksPut({
        "name": self.input,
        "tags" : taglist,
        "sort_criteria": self.sortOrder,
        "sort_ascending": false,
      }, (error, data, response) => {
        if (error == 'Error: Unauthorized') {
          localStorage.removeItem('Authorization');
          this.$router.push('/receiverlogin');
        }
        let res = JSON.parse(response['text'])
        console.log(res)
        let taskslist = res['tasks']
        var counter = 0
        taskslist.forEach(function(element) {
          let _type = '';
          let _tags = '';
          let _credits = element['credits'];
          let task_tags = element['tags'];
          console.log(element)
          for (var k = 0; k < task_tags.length; k++) {
            _tags += task_tags[k];
            if (k != task_tags.length - 1) {
              _tags += ", ";
            }
            if (task_tags[k] == "文字分类" || task_tags[k] == "图片分类" || task_tags[k] == "图片打标" || task_tags[k] == "音频分类")
              _type = task_tags[k];
          }
          var c = { task_id:element['task_id'], name:element['name'], credits:_credits, type:_type, tags:_tags, cover:''}
          self.projectsList.push(c)
          var index = counter;
          counter++;
          self.task.getCoverTasksTaskIdCoverImageGet(element['task_id'], (error, data, response) => {
            if (response.status == 400){
              self.projectsList[index].cover = '../default_cover.jpeg'
            } else {
              let binaryData = [];
              binaryData.push(response.body);
              let imageObjectURL = window.URL.createObjectURL(new Blob(binaryData));
              // let imageObjectURL = window.URL.createObjectURL(response.body);
              self.imageObject = imageObjectURL
              self.projectsList[index].cover = self.imageObject
            }
          })
        })
      })
    },
  }
}
</script>

<style scoped>
@import '@/assets/font/font.css';

.all {
  min-width: 1000px;
}

.top_nav {
    background-color: #fff;
    border-bottom: 1.2px solid rgba(0,0,0,.1);
    box-sizing: border-box;
    display: flex;
    height: 50px;
    position: sticky;
    top: 0;
    z-index: 1000;
}
.top_nav_trigger {
    align-items: center;
    box-shadow: 1.2px 0 0 0 rgb(0 0 0 / 10%);
    box-sizing: border-box;
    display: flex;
    min-width: 230px;
    max-width: 230px;
    padding-left: 20px;
}
.page_title {
    align-items: center;
    box-sizing: border-box;
    display: flex;
    justify-content: space-between;
    padding-left: 20px;
    min-width: 120px;
    flex: 1;
}
.my_account {
    align-items: center;
    align-self: center;
    cursor: pointer;
    display: flex;
    justify-content: center;
    position: relative;
    margin-right: 17px;
}

.logo{
  vertical-align: middle;
  text-align: left;
  font-family: 'Lobster';
  font-size: 22px;
  color:black;
  padding: 8px;
}
.title{
  vertical-align: middle;
  text-align: left;
  font-size: 16px;
  font-weight: bold;
  color:black;
}
.body{
    display: flex;
    flex: 1;
    flex-direction: row;
    min-height: 100%;
    min-width: 100%;
}

.left_nav {
    max-width: 230px;
    min-width: 230px;
    box-shadow: 1.2px 0 0 0 rgb(0 0 0 / 10%);
    box-sizing: border-box;
    flex-direction: column;
    position: relative;
}
.left_nav_list_top {
    box-sizing: border-box;
    list-style-type: none;
    flex: 1;
    flex-direction: column;
    margin: 0;
    padding: 12px;
    height: calc(100vh - 50px - 132.2px);
    min-height: 230px;
}
.left_nav_list_bottom {
    box-sizing: border-box;
    list-style-type: none;
    border-top: 1.2px solid rgba(0,0,0,.1);
    flex: 1;
    flex-direction: column;
    position: relative;
    bottom: 0;
    margin: 0;
    padding: 12px;
}
.left_nav_spacer {
    height: calc(100vh - 329.2px);
    flex: 1;
}
.left_nav_list_item {
    box-sizing: border-box;
    display: flex;
    align-items: center;
    border-radius: 10px;
    color: rgba(0,0,0,.6);
    cursor: pointer;
    font-size: 16px;
    height: 46px;
    padding: 0 13px;
    text-decoration: none;
    white-space: nowrap;
    margin: 5px 0px;
}
.left_nav_list_item:hover {
    background-color: rgba(0,0,0,.06);
}
.left_nav_list_item_active {
    background-color: rgba(84,47,238,.14);
    color: rgba(84,47,238,1);
    pointer-events: none;
}
.list_item_title {
    padding: 15px;
    font-size: 15px;
}

.main_body {
    box-sizing: border-box;
    flex-direction: column;
    position: relative;
    display: flex;
    flex:1;
    height: calc(100vh - 50px);
    min-height: 140px;
}
::v-deep .el-button--primary {
  margin-top: 40px;
  margin-right: 80px;
  padding: 0px 20px;
  border-width: 0px;
  border-radius: 0px 4px 4px 0px;
  background-color: #5D3BE6;
  font-size: 20px;
  min-width: 80px;
}

::v-deep .el-button--primary:hover{
  background-color: rgba(84,47,238,.8);
}

::v-deep .el-button--primary:focus {
  background-color: #5D3BE6;
}

.filter {
  flex-direction: row;
  display: flex;
  align-items:center;
  padding: 30px 60px 10px 40px;
  border-bottom: 1.2px solid rgba(0,0,0,.1);
}
.title_filter {
  padding: 0px;
  font-size: 14px;
  color:rgba(0,0,0,.6);
}
::v-deep .el-radio-group {
  border-color: #5D3BE6;
  margin-left: 10px;
}
::v-deep .el-radio-button__inner {
  background: #fff;
  border-color: #5D3BE6;
  color:#5D3BE6;
  font-size: 12.5px;
  min-width: 80px;
  align-items:center;
  box-shadow:none;
  outline: none;
}
::v-deep .el-radio-button__orig-radio:hover + .el-radio-button__inner {
  background: #5D3BE6;
  border-color: #5D3BE6;
  color: #fff;
}
::v-deep .el-radio-button__orig-radio:checked + .el-radio-button__inner{
  background: #5D3BE6;
  border-color: #5D3BE6;
  box-shadow:none;
  color: #fff;
}

.order_by {
  flex-direction: row;
  display: flex;
  align-items:center;
  margin: 0px 60px 0px 60px;
}
.title_order_by {
  padding: 0px;
  font-size: 14px;
  color:rgba(0,0,0,.6);
}

.scroll_view {
  /*border-top: 0.5px solid rgba(0,0,0,.1);*/
  height: calc(100vh - 140px);
  min-height: 225px;
}

.scroll_element {
  height: fit-content;
  border-bottom: 1.2px solid rgba(0,0,0,.1);
  flex-direction: row;
  display: flex;
  padding: 20px 25px;
}

.scroll_element_text {
  margin: 0px 20px;
  flex-direction: column;
  display: flex;
  cursor: pointer;
  align-items: flex-start;
}
.project_title {
  margin: 0px 0px 3px 0px;
}
.project_detail {
  margin: 0px;
  font-size: 10px;
  color: rgba(0,0,0,.7);
}
.project_image {
  height: 87px;
  width: 100px;
  border-radius: 10%;
  align-self:center;
}

.profile {
  height: 28px;
  width: 28px;
  border-radius: 50%;
}

.message {
  margin: 30px 0px;
}
.message_text {
  font-size: 16px;
  font-weight: bold;
  color: rgba(0,0,0,.2)
}
</style>