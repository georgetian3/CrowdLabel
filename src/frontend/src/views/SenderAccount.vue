<template>
  <div class="all">
    <div class="top_nav">
      <div class="top_nav_trigger">
        <a aria-current="page" class="back_button" data-external="true" href="/sendermission">
          <img src="../assets/back.png" height="18" width="18">
            <p class="list_item_title">返回任务大厅</p>
        </a>
      </div>
      <div class="page_title">
        <h3 class="title">个人信息</h3>
      </div>
    </div>
    <div class="body">
        <div class="left_nav">
            <ul class="left_nav_list_top">
                <li>
                    <a aria-current="page" class="left_nav_list_item left_nav_list_item_active" data-external="true" href="/sendermission">
                        <img src="../assets/my_account_2_active.png" height="21" width="20">
                        <p class="list_item_title">个人信息</p>
                    </a>
                </li>
                <li tag="li" class="left_nav_spacer">
                </li>
            </ul>
            <ul class="left_nav_list_bottom">
                <li>
                    <a aria-current="page" class="left_nav_list_item" data-external="true" href="/settings">
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
            <div class="user_info_row">
              <img class="profile_pic" :src="mainProfile"/>
              <div class="user_info_column">
                <p class="username">{{ userid }}</p>
                <p class="user_info_line">邮箱：{{useremail}}</p>
                <p class="user_info_line">密码：********</p>
                <p class="user_info_line">积分：{{ usercredits }}</p>
              </div>
            </div>
            <div class="button_row">
                <a href="/editmyaccount">
                  <el-button type="primary" plain>编辑个人信息</el-button>
                </a>
                <a href="/sendercredits">
                  <el-button type="primary">我的积分</el-button>
                </a>
                <el-button type="primary" plain icon="el-icon-close" @click="logout">退出登录</el-button>
            </div>
        </div>
    </div>
  </div>
</template>


<script>
import { ApiClient } from '@/crowdlabel-api/src';
import { UsersApi } from '@/crowdlabel-api/src';
import { AuthApi } from '@/crowdlabel-api/src';
export default {
  data() {
    return {
      useremail:'',
      userid:'',
      userpic: '',
      usercredits: '',
      user:'',
      client: '',
      auth: '',
      mainProfile: '',
    };
  },
  mounted () {
    let self = this
    let base = this.$root.basePath
    var apiClient  = new ApiClient(base);
    apiClient.authentications['OAuth2PasswordBearer'].accessToken = localStorage.getItem('Authorization')
    self.client = apiClient
    var usersApi = new UsersApi(apiClient);
    self.user = usersApi
    var authApi = new AuthApi(apiClient);
    this.auth = authApi
    self.user.getMeUsersMeGet((error, data, response) => {
      if (error == 'Error: Unauthorized') {
        localStorage.removeItem('Authorization');
        this.$router.push('/senderlogin');
        return;
      }
      let a = JSON.parse(response['text'])
      console.log(a)
      if (a.user_type != 'requester'){
        localStorage.removeItem('Authorization');
        this.$router.push('/');
        return;
      }
      self.userid = a.username
      self.usercredits = a.credits
      self.useremail = a.email
    })
    self.user.getPfpUsersMeProfilePictureGet((error, data, response) => {
      if (response.status == 404){
        self.mainProfile = '../my_account.svg'
      } else {
        let binaryData = [];
        binaryData.push(response.body);
        let imageObjectURL = window.URL.createObjectURL(new Blob(binaryData));
        self.mainProfile = imageObjectURL
      }
    })
  },
  methods: {
    refresh: function() {
      let self = this
      self.user.getMeUsersMeGet((error, data, response) => {
      if (error == 'Error: Unauthorized') {
        localStorage.removeItem('Authorization');
        this.$router.push('/senderlogin');
        return;
      }
      let a = JSON.parse(response['text'])
      self.userid = a['username']
      self.usercredits = a['credits']
      })
    },
    logout () {
      let self = this
      self.$confirm('您即将退出当前登录?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info',
      }).then(() => {
        self.auth.logoutLogoutPost((error, data, response) => {
          console.log("succesfully logout")
          localStorage.removeItem('Authorization');
          self.$router.push('/');
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消退出登录'
        });
      });
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
    cursor: pointer;
    display: flex;
    min-width: 230px;
    max-width: 230px;
    padding-left: 10px;
}
.back_button {
    box-sizing: border-box;
    display: flex;
    align-items: center;
    border-radius: 10px;
    color: rgba(0,0,0,.7);
    cursor: pointer;
    font-size: 16px;
    height: 40px;
    text-decoration: none;
    white-space: nowrap;
    padding: 0px 10px;
}
.back_button:hover {
  background-color: rgba(0,0,0,.06);
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
    display: flex;
    justify-content: center;
    margin-left: 10px;
    margin-right: 20px;
    position: relative;
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
    min-height: 135px;
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
.left_nav_list_item_active:hover {
    background-color: rgba(0,0,0,.06);
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
}
.search_bar {
    box-sizing: border-box;
    flex-direction: row;
}

.username{
  vertical-align: middle;
  text-align: left;
  font-size: 22px;
  font-weight: bold;
  color:black;
  margin: 5px 5px 10px 5px;
}
.user_info_row {
  text-align: left;
  margin-left: 100px;
  margin-top: 80px;
  display: flex;
  flex-direction: row;
}
.profile_pic {
  height: 200px;
  width: 200px;
  border-radius: 50%;
}
.user_info_column {
  align-self: center;
  margin: 0px 50px 10px 50px;
  display: flex;
  flex-direction: column;
}
.user_info_line {
  margin: 3px;
  display: flex;
  flex-direction: column;
}

.button_row {
  text-align: left;
  margin: 0px 0px 50px 350px;
}
::v-deep .el-button--primary {
  border-color: #5D3BE6;
  background-color: #5D3BE6;
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
  background-color: #5D3BE6;
  border-color: #5D3BE6;
}
</style>