using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using UnityEngine.UI;
using System.Threading;

public enum GameState 
{
    STAY,
    RUNNING,
    OVER,
};




public class GameManager
{
    private static GameManager ins;
    public Vector3 startPos;
    public Transform carRoot;
    public SocketLinkClient socket;
    public int id;
    public GameState state;
    public Dictionary<int,Car> carList;
    public string chooseCar = "";
    public GameObject CarPrefab;
    public List<string> msgList;

    public static GameManager GetInstance()
    {
        if (ins == null)
        {
            ins = new GameManager();
        }
        return ins;
    }

    // Use this for initialization
    public GameManager()
    {
        socket = GameObject.Find("Socket").GetComponent<SocketLinkClient>();
        startPos = GameObject.Find("Canvas/Panel/StartPos").GetComponent<RectTransform>().anchoredPosition3D;
        carRoot = GameObject.Find("Canvas/Panel/carRoot").transform;
        state = GameState.STAY;
        carList = new Dictionary<int,Car>();
        msgList = new List<string>();
        CarPrefab = (GameObject)Resources.Load("Prefabs/Car");
        GameObject.Find("Canvas/UI/Button1").GetComponent<Button>().onClick.AddListener(ClearCar);
        GameObject.Find("Canvas/UI/Button2").GetComponent<Button>().onClick.AddListener(StartCreateCar);
        GameObject.Find("Canvas/UI/Button3").GetComponent<Button>().onClick.AddListener(ChooseNextFinish);
    }

    public void ChooseNextFinish()
    {
        ClearCarObj();
        SendNextCarList();
    }

    public void ClearCar()
    {
        ClearCarObj();
        SendClear();

    }

    public void ClearCarObj()
    {
        var count = carRoot.transform.childCount;
        for (var i = count - 1; i >= 0; i--)
        {
            GameObject.Destroy(carRoot.transform.GetChild(i).gameObject);
        }
        id = 0;
        carList.Clear();
    }

    public void StartCreateCar()
    {
        for (var i = 0; i < Config.CAR_NUM; i++)
        {
            CreateCar(true);
        }
    }

    public void StartGame()
    {
        id = 0;
        socket.TryConnect();

        state = GameState.RUNNING;

    }

    public void CreateCar(bool isSend)
    {
        var carGo = GameObject.Instantiate(CarPrefab);
        carGo.transform.SetParent(carRoot, false);
        carGo.GetComponent<RectTransform>().anchoredPosition3D = startPos;
        carGo.transform.localRotation = Quaternion.Euler(new Vector3(0, 0, -180));
        carGo.GetComponent<Car>().setIndex(id);
        carList.Add(id, carGo.GetComponent<Car>());
        if (isSend)
        {
            SendCreateCar(id);
        }
        id += 1;
    }

    // Update is called once per frame
    void Update()
    {

    }

    public void SendCreateCar(int index)
    {
        string str = "s"+Config.CMD_CREATE+"," + index.ToString() + "e";
        socket.SendMsgToServer(str);
    }

    public void SendClear()
    {
        string str = "s"+Config.CMD_CLEAR+"e";
        socket.SendMsgToServer(str);
    }


    public void SendMoveMsg(int index ,float[] disList,float speed,float rotationSpeed)
    {
        string str = "s"+Config.CMD_CAR_RUN+",";
        str = str + index.ToString() + ",";
        for (var i = 0; i < 5; i++)
        {
            str = str + disList[i].ToString("f3") + ",";
        }
        str = str + speed.ToString("f3") + ",";
        str = str + rotationSpeed.ToString("f3") + "e";
        socket.SendMsgToServer(str);
        //Debug.Log(str);
    }
    public void OnReceive(string str)
    {
        lock (msgList)
        {
            msgList.Add(str);
        }
        
    }

    public void MsgFliter()
    {
        if (msgList.Count == 0)
        {
            return;
        }
        string[] array = null;
        lock (msgList)
        {
            array = msgList.ToArray();
        }
        
        msgList.Clear();
        for(var index = 0; index < array.Length; index++)
        {
            var str = array[index];
            var ret = MsgFilter(str, new List<string>());
            foreach (var item in ret)
            {
                var cmd = FilerCmd(item);
                //Debug.Log("Receive cmd " + cmd[0]);
                switch (cmd[0])
                {
                    case Config.CMD_CAR_CONTROL:
                        ControlCar(cmd);
                        break;
                    case Config.CMD_NEXT_READY:
                        for (var i = 0; i < Config.CAR_NUM; i++)
                        {
                            CreateCar(false);
                        }
                        break;
                }
            }
        }
    }

    public void ControlCar(string[] cmd)
    {
        var car_id = int.Parse(cmd[1]);
        var dir = int.Parse(cmd[2]);
        var speed = int.Parse(cmd[3]);
        Car car;
        carList.TryGetValue(car_id,out car);
        //Debug.Log("GetID"+  id.ToString());
        if (car)
        {
            car.ControlCar(dir,speed);
        }
    }

    public string[] FilerCmd(string cmd)
    {
        var ret = cmd.Split(',');
        return ret;
    }

    public List<string> MsgFilter(string str,List<string> ret)
    {
        var s_pos = str.IndexOf("s");
        if (s_pos == -1)
            return ret;
        var e_pos = str.IndexOf("e");
        if (e_pos == -1)
        {
            return ret;
        }
        var len = e_pos - s_pos-1;
        
        var data = str.Substring(s_pos+1, len);
        ret.Add(data);
        var last = str.Substring(e_pos+1,str.Length -e_pos-1);
        ret = MsgFilter(last, ret);
        return ret;
    }

    public void ChooseCar(int index)
    {
        if (!chooseCar.Equals(""))
        {
            chooseCar = chooseCar + ",";
        }
        chooseCar = chooseCar + index.ToString();
    }

    public void SendNextCarList()
    {
        string str = "s" + Config.CMD_CHOOSE_CAR + "," + chooseCar + "e";
        socket.SendMsgToServer(str);
        chooseCar = "";
        Debug.Log(str);
    }

}
