using UnityEngine;
using System.Collections;

public class GameStart : MonoBehaviour
{

    // Use this for initialization
    void Start()
    {
        GameManager.GetInstance().StartGame();
    }

    // Update is called once per frame
    void Update()
    {

    }

    private void FixedUpdate()
    {
        GameManager.GetInstance().MsgFliter();
    }
}
