using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System;
using System.Text;

public class SocketLinkClient : MonoBehaviour
{
    private string tempString = "";
    IPEndPoint endPoint;
    // Start is called before the first frame update
    void Start()
    {
        Debug.Log("Start");
        
    }

    Socket socketSend;
    public void TryConnect()
    {
        //try
        //{
        //    int _port = 30000;
        //    string _ip = "127.0.0.1";

        //    //创建客户端Socket，获得远程ip和端口号
        //    socketSend = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
        //    IPAddress ip = IPAddress.Parse(_ip);
        //    IPEndPoint point = new IPEndPoint(ip, _port);
        //    socketSend.Connect(point);
        //    Debug.Log("连接成功!");
        //    StartCoroutine(CallRece());
        //}
        //catch (Exception)
        //{
        //    Debug.Log("IP或者端口号错误...");
        //}

        try
        {
            int _port = 30000;
            string _ip = "127.0.0.1";
            socketSend = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            SocketAsyncEventArgs args = new SocketAsyncEventArgs();//创建连接参数对象
            this.endPoint = new IPEndPoint(IPAddress.Parse(_ip), _port);
            args.RemoteEndPoint = this.endPoint;
            args.Completed += OnConnectedCompleted;//添加连接创建成功监听
            socketSend.ConnectAsync(args); //异步创建连接
        }
        catch (Exception e)
        {
            Debug.Log("服务器连接异常:" + e);
        }
    }

    private void OnConnectedCompleted(object sender, SocketAsyncEventArgs args)
    {
        try
        {   ///连接创建成功监听处理
            if (args.SocketError == SocketError.Success)
            {
                Debug.Log("网络连接成功线程：" + Thread.CurrentThread.ManagedThreadId.ToString());
                StartReceiveMessage(); //启动接收消息
            }
        }
        catch (Exception e)
        {
            Debug.Log("开启接收数据异常" + e);
        }

    }


    private void StartReceiveMessage()
    {

        //启动接收消息
        SocketAsyncEventArgs receiveArgs = new SocketAsyncEventArgs();
        //设置接收消息的缓存大小，正式项目中可以放在配置 文件中
        byte[] buffer = new byte[1024 * 1024 * 10];
        //设置接收缓存
        receiveArgs.SetBuffer(buffer, 0, buffer.Length);
        receiveArgs.RemoteEndPoint = this.endPoint;
        receiveArgs.Completed += OnReceiveCompleted; //接收成功
        socketSend.ReceiveAsync(receiveArgs);//开始异步接收监听
    }

    public void OnReceiveCompleted(object sender, SocketAsyncEventArgs args)
    {
        try
        {
            //Debug.Log("网络接收成功线程：" + Thread.CurrentThread.ManagedThreadId.ToString());

            if (args.SocketError == SocketError.Success && args.BytesTransferred > 0)
            {
                //创建读取数据的缓存
                byte[] bytes = new byte[args.BytesTransferred];
                //将数据复制到缓存中
                Buffer.BlockCopy(args.Buffer, 0, bytes, 0, bytes.Length);
                string str = Encoding.UTF8.GetString(bytes, 0, bytes.Length);
                GameManager.GetInstance().OnReceive(str);
                //再次启动接收数据监听，接收下次的数据。
                StartReceiveMessage();
            }
        }
        catch (Exception e)
        {
            Debug.Log("接收数据异常：" + e);
        }
    }


    //IEnumerator CallRece()
    //{
    //    while (true)
    //    {
    //        try
    //        {
    //            Debug.Log("len 1");
    //            byte[] buffer = new byte[1024 * 1024 * 3];
    //            //实际接收到的有效字节数
    //            int len = socketSend.Receive(buffer);
    //            if (len != 0)
    //            {
    //                Debug.Log("len " + len.ToString());
    //                string str = Encoding.UTF8.GetString(buffer, 0, len);
    //                //GameManager.GetInstance().OnReceive(str);
    //            }

    //        }
    //        catch { }
    //        yield return new WaitForSeconds(0.1f);
    //    }
    //}


    /// <summary>
    /// 向服务器发送消息
    /// </summary>
    /// <param name="sender"></param>
    /// <param name="e"></param>
    public void SendMsgToServer(string str)
    {
        if (tempString.Length >1000)
        {
            Flush();
        }
        tempString = tempString + str;
    }

    public void Flush()
    {
        if (tempString.Equals(""))
        {
            return;
        }
        try
        {
            string msg = tempString;
            var buffer = Encoding.UTF8.GetBytes(msg);
            socketSend.Send(buffer);
        }
        catch { }
        tempString = "";
    }

    // Update is called once per frame
    private void FixedUpdate()
    {
        Flush();
    }

}
