using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using UnityEngine.UI;

public class Car : MonoBehaviour
{
    public float speed;//运行速度
    public float addSpeed;//向前的加减速度
    public float addSpeed2;//加速度增加值
    public Vector2  dir;//方向
    public RectTransform rectTrans;
    public float rotationSpeed;
    public float addRotationSpeed;
    public bool isAlive;
    public int index;

    public void setIndex(int index)
    {
        this.index = index;
    }

    public void MoveCar(float time)
    {
        var dis = time * speed;
        var nor_dir = dir.normalized;
        var move_x = nor_dir.x* dis;
        var move_y = nor_dir.y * dis;
        rectTrans.anchoredPosition += new Vector2(move_x,move_y);
    }

    public void UpdateSpeed()
    {
        speed = addSpeed + speed;
        if( Mathf.Abs( rotationSpeed + addRotationSpeed) < 5)
            rotationSpeed = rotationSpeed + addRotationSpeed;
    }

    public void AddSpeed()
    {
        addSpeed = 1f;
    }

    public void SubSpeed()
    {
        addSpeed = -1;
    }

    public void HoldSpeed()
    {
        addSpeed = 0;
        addSpeed2 = 0;
    }

    public void Left()
    {
        addRotationSpeed = 0.3f;
    }

    public void Right()
    {
        addRotationSpeed = -0.3f;
    }

    public void HoldDir()
    {
        addRotationSpeed = 0;
        rotationSpeed = 0;
    }

    public void ControlCar(int dir ,int speed)
    {
        switch (dir)
        {
            case 0:
                HoldDir();
                break;
            case -1:
                Right();
                break;
            case 1:
                Left();
                break;
        }

        switch (speed)
        {
            case 0:
                HoldSpeed();
                break;
            case -1:
                SubSpeed();
                break;
            case 1:
                AddSpeed();
                break;
        }
    }

    // Use this for initialization
    void Start()
    {
        rectTrans =  this.gameObject.GetComponent<RectTransform>();
        dir = this.transform.up;
        rotationSpeed = 0;
        addSpeed = 0;
        isAlive = true;
        speed = 1;
        this.gameObject.GetComponent<Button>().onClick.AddListener(OnClick);
    }

    public void OnClick()
    {
        this.gameObject.GetComponent<Image>().color = Color.blue;
        this.gameObject.GetComponent<Button>().interactable = false;
        GameManager.GetInstance().ChooseCar(this.index);
    }

    // Update is called once per frame
    void LateUpdate()
    {
        if (!isAlive)
        {
            return;
        }
        MoveCar(Time.deltaTime);
    }

    private void FixedUpdate()
    {
        if (!isAlive)
        {
            return;
        }

        if (GameManager.GetInstance().state != GameState.RUNNING)
        {
            return;
        }
        //Debug.Log(transform.up);
        UpdateSpeed();
        UpdateRotation();

        var ret = RayLine();
       GameManager.GetInstance().SendMoveMsg(index,ret,speed/100,rotationSpeed/10);
    }

    public void UpdateRotation()
    {
        if (speed == 0)
        {
            return;
        }
        var rotation = this.rectTrans.localRotation.eulerAngles;
        var z = rotation.z + rotationSpeed;
        this.rectTrans.localRotation = Quaternion.Euler(new Vector3(rotation.x, rotation.y, z));
        dir = this.transform.up;
    }

    private void OnCollisionEnter2D(Collision2D collision)
    {
        isAlive = false;
    }


    public float[] RayLine()
    {
        var ret = new float[5];
        RaycastHit2D hit = Physics2D.Raycast((Vector2)transform.position, (Vector2)transform.up, 1000, LayerMask.GetMask("Road"));
        if (hit.collider)
        {
            Debug.DrawLine(transform.position, (Vector3)hit.point, Color.red);
            ret[0] = ((Vector2)transform.position - hit.point).magnitude;
        }

        var vec1 = Quaternion.AngleAxis(-45,Vector3.forward) *transform.up;
        RaycastHit2D hit_1 = Physics2D.Raycast((Vector2)transform.position, (Vector2)vec1, 1000, LayerMask.GetMask("Road"));
        if (hit_1.collider)
        {
            Debug.DrawLine(transform.position, (Vector3)hit_1.point, Color.red);
            ret[1] = ((Vector2)transform.position -hit_1.point).magnitude;
        }

        var vec2 = Quaternion.AngleAxis(45, Vector3.forward) * transform.up;
        RaycastHit2D hit_2 = Physics2D.Raycast((Vector2)transform.position, (Vector2)vec2, 1000, LayerMask.GetMask("Road"));
        if (hit_2.collider)
        {
            Debug.DrawLine(transform.position, (Vector3)hit_2.point, Color.red);
            ret[2] = ((Vector2)transform.position - hit_2.point).magnitude;
        }

        RaycastHit2D hit_3 = Physics2D.Raycast((Vector2)transform.position, (Vector2)transform.right, 1000, LayerMask.GetMask("Road"));
        if (hit_3.collider)
        {
            Debug.DrawLine(transform.position, (Vector3)hit_3.point, Color.red);
            ret[3] = ((Vector2)transform.position - hit_3.point).magnitude;
        }

        RaycastHit2D hit_4 = Physics2D.Raycast((Vector2)transform.position, -(Vector2)transform.right, 1000, LayerMask.GetMask("Road"));
        if (hit_4.collider)
        {
            Debug.DrawLine(transform.position, (Vector3)hit_4.point, Color.red);
            ret[4] = ((Vector2)transform.position - hit_4.point).magnitude;
        }
        return ret;
    }
}
