<template>
  <div class="all">
    <div class="top_nav">
      <div class="top_nav_trigger">
        <img src="../assets/label.png" alt="label" height="26">
        <h2 class="logo">CrowdLabel</h2>
      </div>
      <div class="page_title">
        <h3 class="title">任务名称</h3>
      </div>
    </div>
    <div class="body">
      <div class="left_nav">
        <ul class="left_nav_list_top">
          <li>
            <a aria-current="page" class="left_nav_list_item left_nav_list_item_active" data-external="true" href="/projects">
              <p class="list_item_title">任务信息</p>
              <img class="down_arrow" src="../assets/down_arrow_active.png" height="20" width="20">
            </a>
          </li>
        </ul>
        <div class="project_description">
          <p class="text_bold">任务简介：</p>
           <p id="task_brief" class="text_normal"></p>
           <!-- div class="placeholder_text"></div> -->
            <p class="text_bold"><br />任务类型：</p><p class="text_normal">{{ task_type }}</p>
            <p class="text_bold"><br />任务标签：</p><p class="text_normal" id="tags"></p>
            <p class="text_bold"><br />问题数量：</p><p class="text_normal">{{ task_question_num }}</p>
            <p class="text_bold"><br />积分奖励：</p><p class="text_normal">{{ task_credit }}</p>
            <div class="placeholder_border"></div>
        </div>
      </div>
      <div class="main_body">
        <div class="instruction">
          <p class="text_bold" id="question_title">问题{{cur_question + 1}}：</p>
          
          <p class="text_normal" id="question_prompt"></p>
        </div>
        <div class="scroll_view">
          <el-scrollbar style="height: 100%">
            <p class="text_normal" id="question_text">
            </p>
          </el-scrollbar>
        </div>
        <div id="answers">
          <!--单选题-->
          <el-radio-group v-model="radio" id="singleChoiceOptions">
            <el-radio :label="item.value" @change="handleChange_singleChoice" v-for="(item,index) in choicesGiven">{{item.label}}</el-radio>
          </el-radio-group>
          <!--多选题-->
          <el-checkbox-group v-model="checkList" id="multiChoiceOptions">
            <el-checkbox :label="item.value" :key="index" @change="handleChange_multiChoice" v-for="(item,index) in choicesGiven">{{item.label}}</el-checkbox>
          </el-checkbox-group>
          <!--开放题-->
          <el-input
            id="openAnswerBox"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 12}"
            placeholder="请输入内容"
            v-model="textarea">
          </el-input>
        </div>
        <div class="footer">
          <el-button id="quit_button" type="primary" v-on:click="quit()" plain>退出答题</el-button>
          <a>
            <el-button id="prev_button" type="primary" :disabled="isFirstQuestion" v-on:click="prevQuestion()">&lt 上一题</el-button>
          </a>
          <el-button id="next_button" type="primary" v-on:click="nextQuestion()">下一题 ></el-button>
        </div>
        <el-progress :percentage="percentage" :color="customColor"></el-progress>
      </div>
    </div>
  </div>
</template>


<script>
import { ApiClient } from '@/crowdlabel-api/src';
import { UsersApi } from '@/crowdlabel-api/src';
import { TasksApi } from '@/crowdlabel-api/src';
import { QuestionsApi } from '@/crowdlabel-api/src';
export default {
  data() {
    return {
      user: '',
      client: '',
      task_id: '',
      task_name: '',
      task_type: '',
      task_tags: [],
      task_brief: '',
      task_cover: '',
      task_credit: '',
      task_question_num: '',
      task_map: [],
      question: '',
      cur_question: 0,
      question_id: 0,
      question_type: '',
      prompt: '',
      percentage: 0,
      customColor: '#5D3BE6',
      radio: -1,
      checkList: [],
      textarea: '',
      choicesGiven: [],
      isFirstQuestion: false
    };
  },
  mounted() {
    let self = this
    let base = this.$root.basePath
    self.task_id = localStorage.getItem('TaskID')
    var apiClient  = new ApiClient(base);
    apiClient.authentications['OAuth2PasswordBearer'].accessToken = localStorage.getItem('Authorization');
    self.client = apiClient;
    var usersApi = new UsersApi(apiClient);
    self.user = usersApi;
    var tasksApi = new TasksApi(apiClient);
    self.task = tasksApi;
    self.task_map = JSON.parse(localStorage.getItem('QuestionList'))
    self.task_type = localStorage.getItem('TaskType');
    var questionsApi = new QuestionsApi(apiClient);
    self.question = questionsApi;
    self.cur_question = parseInt(localStorage.getItem('QuestionIndex'))
    console.log("QUESTION INDEX: " + self.cur_question);
    self.question_id = self.task_map[this.cur_question];
    var my_username = "";
    // 判断当前是否是第一题，如是则disable“上一题”按钮
    if (self.cur_question == 0)
      self.isFirstQuestion = true;
    self.user.getMeUsersMeGet((error, data, response) => {
      let res = JSON.parse(response['text']);
      my_username = res.username;
      if (error == 'Error: Unauthorized') {
        localStorage.removeItem('Authorization');
        this.$router.push('/senderlogin');
        return;
      }
    })
    self.task.getTaskTasksTaskIdGet(self.task_id, (error, data, response) => {
      let res = JSON.parse(response['text'])
      self.task_amount = res.responses_required;
      self.task_brief = res.introduction;
      self.task_name = res.name;
      self.task_tags = eval(res.tags);
      self.task_credit = res.credits;
      self.task_question_num = res.questions.length;
      // 填充任务简介
      if (res.introduction == "")
        document.getElementById("task_brief").innerHTML = "该发布者暂未提供简介";
      else
        document.getElementById("task_brief").innerHTML = self.task_brief;
      // 填充任务标签
      var tags_str = "";
      for (var i = 0; i < self.task_tags.length; i++) {
        tags_str += self.task_tags[i];
        if (i != self.task_tags.length - 1) {
          tags_str += ", ";
        }
      }
      document.getElementById("tags").innerHTML = tags_str;
      // 计算任务进度条
      self.percentage = parseInt((((self.cur_question) / self.task_question_num) * 100).toFixed(0));
      // 判断当前是否是最后一题，如是则将“下一题”按钮更改为“完成任务”按钮
      if (self.cur_question == self.task_question_num - 1) {
        document.getElementById("next_button").innerHTML = "完成任务";
      }

    })
    console.log("QUESTION ID: " + self.question_id)
    console.log("TASK ID: " + self.task_id)
    self.question.getQuestionTasksTaskIdQuestionsQuestionIdGet(self.task_id, self.question_id, (error, data, response) => {
      let res = JSON.parse(response['text']);
      // 填充问题
      self.prompt = res.prompt;
      document.getElementById("question_prompt").innerHTML = self.prompt;
      // 填充答题选项
      console.log(res);
      self.question_type = res.question_type;
      if (self.question_type == "single_choice") { // 单选题
        console.log("QUESTION TYPE: single_choice")
        var list_choices = res.options;
        for (var i = 0; i < list_choices.length; i++) {
          var k = { label: list_choices[i], value: i };
          self.choicesGiven.push(k);
        }
        document.getElementById("multiChoiceOptions").remove();
        document.getElementById("openAnswerBox").remove();
      } else if (self.question_type == "multi_choice") { // 多选题
        console.log("QUESTION TYPE: multi_choice")
        // 调整margin以避免UI错乱
        document.getElementById("answers").style.marginTop = "20px";
        var list_choices = res.options;
        for (var i = 0; i < list_choices.length; i++) {
          var k = { label: list_choices[i], value: i };
          self.choicesGiven.push(k);
        }
        document.getElementById("singleChoiceOptions").remove();
        document.getElementById("openAnswerBox").remove();
      } else if (self.question_type == "open") { // 开放题
        console.log("QUESTION TYPE: open")
        document.getElementById("singleChoiceOptions").remove();
        document.getElementById("multiChoiceOptions").remove();
      } else {
        console.log("QUESTION TYPE ERROR");
      }
      
      console.log("PREVIOUS ANSWERS:")
      console.log(res.answers)
      // 如已回答过该题，填充答案
      for (var i = 0; i < res.answers.length; i++) {
        let cur_answer = res.answers[i];
        console.log(cur_answer)
        console.log(cur_answer.answer)
        console.log(cur_answer.respondent)
        if (cur_answer.respondent == my_username) { // 当前用户已回答
          if (self.question_type == "single_choice") {
            self.radio = cur_answer.answer.choice;
          } else if (self.question_type == "multi_choice") {
            self.checkList = cur_answer.answer.choices;
          } else if (self.question_type == "open") {
            self.textarea = cur_answer.answer.text;
          }
        }
      }
        
    })
    self.question.getQuestionResourceTasksTaskIdQuestionsQuestionIdResourceGet(self.task_id, self.question_id, (error, data, response) => {
        response.body.text().then((text) => {
            document.getElementById("question_text").innerHTML = text;
        });
    })
    self.task.getProgressTasksTaskIdProgressGet(self.task_id, (error, data, response) => {
      let res = JSON.parse(response['text']);
      var progress = res.progress;
      console.log("TASK PROGRESS: " + progress)
    })
    
    
  },
  methods: {
    alertMessage() {
        this.$message({
          showClose: true,
          message: '您尚未作答本题目，请先完成本题。',
          type: 'warning'
        });
    },
    prevQuestion() {
      // 上传答案
      var answer;
      if (this.question_type == "single_choice") {
        let _radio = this.radio;
        answer = {"choice": _radio};
      }
      else if (this.question_type == "multi_choice") {
        let _checkList = this.checkList;
        answer = {"choices": _checkList};
      }
      else if (this.question_type == "open") {
        let _textarea = this.textarea;
        console.log(_textarea);
        answer = {"text": _textarea};
      }
      this.question.createAnswerTasksTaskIdQuestionsQuestionIdAnswerPut(this.task_id, this.question_id, answer, (error, data, response) => {
        this.$store.commit('changeQuestionIndex', this.cur_question - 1);
        document.location.href = '/question_text';
      })
      
    },
    nextQuestion() {
      let _radio = this.radio;
      let _checkList = this.checkList;
      let _textarea = this.textarea;
      if (this.question_type == "single_choice" && _radio == -1) {
        this.alertMessage();
      } else if (this.question_type == "multi_choice" && _checkList.length == 0){
        this.alertMessage();
      } else if (this.question_type == "open" && _textarea == "") {
        this.alertMessage();
      } else {
          // 上传答案
          var answer;
          if (this.question_type == "single_choice") {
            answer = {"choice": _radio};
          }
          else if (this.question_type == "multi_choice") {
            answer = {"choices": _checkList};
          }
          else if (this.question_type == "open") {
            answer = {"text": _textarea};
          }
          this.question.createAnswerTasksTaskIdQuestionsQuestionIdAnswerPut(this.task_id, this.question_id, answer, (error, data, response) => {
            // 判断跳转到什么页面
            if (this.cur_question + 1 == this.task_question_num) { // 最后一题
              // 弹窗
              this.$confirm('确认完成任务？', '完成任务', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'info'
              }).then(() => {
                this.$store.commit('changeQuestionIndex', this.cur_question + 1);
                this.task.completeTasksTaskIdCompletePost(this.task_id, (error, data, response) => {
                  document.location.href = '/mission_complete';
                });
              }).catch(() => {
              });
            } else {
              this.$store.commit('changeQuestionIndex', this.cur_question + 1);
              document.location.href = '/question_text';
            }
          })
        }
    },
    handleChange_singleChoice(val) {
      this.radio = val;
      console.log(this.radio);
    },
    handleChange_multiChoice() {
      console.log(this.checkList);
    },
    quit() {
        // 弹窗
        this.$confirm('确认退出任务？您的答题记录将被自动保存。', '退出任务', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        }).then(() => {
          this.$alert('您的答题记录已保存至草稿箱', '退出成功', {
            confirmButtonText: '好的',
            callback: action => {
              // 上传当前题的答案
              var answer;
              var is_answered = false; // 当前题目是否已回答，答了再存
              if (this.question_type == "single_choice") {
                let _radio = this.radio;
                if (_radio != -1) {
                  is_answered = true;
                  answer = {"choice": _radio};
                }
              }
              else if (this.question_type == "multi_choice") {
                let _checkList = this.checkList;
                if (_checkList.length > 0) {
                  is_answered = true;
                  answer = {"choices": _checkList};
                }
              }
              else if (this.question_type == "open") {
                let _textarea = this.textarea;
                if (_textarea != "") {
                  is_answered = true;
                  answer = {"text": _textarea};
                }
              }
              if (is_answered) {
                this.question.createAnswerTasksTaskIdQuestionsQuestionIdAnswerPut(this.task_id, this.question_id, answer, (error, data, response) => {
                  document.location.href = '/projects';
                })
              } else {
                document.location.href = '/projects';
              }
            }
          });
        }).catch(() => {
        });
      }
  },
  
}



</script>

<style scoped>
@import '@/assets/font/font.css';

.all {
  min-width: 1150px;
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
    min-width: 300px;
    max-width: 300px;
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
}

.left_nav {
    max-width: 300px;
    min-width: 300px;
    box-shadow: 1.2px 0 0 0 rgb(0 0 0 / 10%);
    box-sizing: border-box;
    flex-direction: column;
    /* height: calc(100vh - 50px); */
    min-height: 630px;
}
.left_nav_list_top {
    box-sizing: border-box;
    list-style-type: none;
    flex: 1;
    flex-direction: column;
    margin: 0;
    padding: 12px;
}
.down_arrow {
  margin-left: 140px;
}
.placeholder_text {
  height: 5px;
}
.placeholder_border {
  height: 20px;
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
    padding: 10px;
    font-size: 15px;
}
.project_description {
  text-align: left;
  font-size: 14px;
  padding: 0px 20px;
  border-bottom: 1.2px solid rgba(0,0,0,.1);
}
.text_bold {
  font-weight: bold;
  margin: 0px;
  display:inline;
}
.text_normal {
  font-weight: normal;
  margin: 0px;
  line-height: 1.5;
  display:inline;
}

.main_body {
    box-sizing: border-box;
    flex-direction: column;
    position: relative;
    display: flex;
    flex:1;
}

.instruction {
  text-align:left;
  padding: 35px 40px 0px 40px;
}
.scroll_view {
  border: 1.2px solid rgba(0,0,0,.1);
  margin: 30px 80px 30px 70px;
  padding: 15px 15px;
  height: calc(100vh - 390px);
  min-height: 300px;
  text-align: left;
  background-color: rgba(84,47,238,.08);
}

.question {
  text-align: left;
  font-size: 18px;
  font-weight: bold;
  padding-left: 45px;
}

::v-deep .el-button--primary {
  border-color: #5D3BE6;
  background-color: #5D3BE6;
  border-radius: 8px;
  margin-right: 10px;
}
::v-deep .el-button--primary:hover{
  background-color: rgba(84,47,238,.7);
  border-color: rgba(84,47,238,.1);
}
::v-deep .el-button--primary:focus {
  background-color: #5D3BE6;
  border-color: #5D3BE6;
}

::v-deep .el-button--primary.is-plain {
  border-color: #5D3BE6;
  color: #5D3BE6;
  background-color: #fff;
}
::v-deep .el-button--primary.is-plain:hover{
  background-color: #5D3BE6;
  border-color: #5D3BE6;
}
::v-deep .el-button--primary.is-plain:focus {
  border-color: #5D3BE6;
  color: #5D3BE6;
  background-color: #fff;
}
::v-deep .el-button--primary.is-disabled {
  border-color: #5D3BE6;
  background-color: #5D3BE6;
  border-radius: 8px;
  margin-right: 10px;
}
::v-deep .el-button--primary.is-disabled:hover {
  border-color: #5D3BE6;
  background-color: #5D3BE6;
  border-radius: 8px;
  margin-right: 10px;
}
#answers {
  margin: 10px 0px 20px 0px;
}
::v-deep .el-radio-group {
  transform:scale(1.2);
  font-size:30px !important;
}
::v-deep .el-radio__label {
  color: black;
}
::v-deep .el-radio__input .el-radio__inner {
  border-color: rgba(0, 0, 0, 0.2);
}
/* 选中后radio文本的颜色 */
::v-deep .el-radio__input.is-checked + .el-radio__label {
  color: #5D3BE6;
}
/* radio选中后小圆点的颜色 */
::v-deep .el-radio__input.is-checked .el-radio__inner {
  background: #5D3BE6 !important;
  border-color: #5D3BE6 !important;
}
/* hover时颜色 */
::v-deep .el-radio__inner:hover {
  border-color: #5D3BE6;
}

::v-deep .el-checkbox-group {
  transform:scale(1.1);
}
::v-deep .el-checkbox__label {
  color: black;
}
/* 选中后radio文本的颜色 */
::v-deep .el-checkbox__input.is-checked + .el-checkbox__label {
  color: #5D3BE6;
}
/* radio选中后小圆点的颜色 */
::v-deep .el-checkbox__input.is-checked .el-checkbox__inner {
  background: #5D3BE6 !important;
  border-color: #5D3BE6 !important;
}
/* hover时颜色 */
::v-deep .el-checkbox__inner:hover {
  border-color: #5D3BE6;
}

::v-deep .el-textarea {
  margin: 0px 50px;
  width: 80%;
}
::v-deep .el-textarea__inner:hover {
  width: 100%;
  border-color: #5D3BE6;
}
::v-deep .el-textarea__inner:focus {
  border-color: #5D3BE6;
}
::v-deep .el-progress {
  margin: 25px 0px;
  width: 80% !important;
  align-self:center;
}
.footer {
  text-align:center;
  margin-top:auto;
}

#question_title {
  font-size: 17px;
}

#question_prompt {
  font-size: 17px;
}

</style>