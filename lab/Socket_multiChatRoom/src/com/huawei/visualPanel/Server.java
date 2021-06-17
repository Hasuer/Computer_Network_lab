package com.huawei.visualPanel;

import java.awt.BorderLayout;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import javax.swing.JFrame;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;

public class Server extends JFrame {
	//static List<Socket>ls=new ArrayList<Socket>();
	//static List<String>lname=new ArrayList<String>();
	public static Map<Socket,String> socketsMaps
			= Collections.synchronizedMap(new HashMap<Socket,String>());
	//
	ServerSocket sc=null;
	Socket s=null;
	public JTextArea jta=new JTextArea(10,20);
	public JScrollPane jsp=new JScrollPane(jta);
	public String ServerName="服务器";
	static int number=1;
	Server() throws IOException{
		super();
		setTitle("服务器");
		jta.setEditable(false); //文本显示框不可编辑
		this.add(jsp,BorderLayout.CENTER);
		//默认的设置是超过文本框才会显示滚动条,以下设置让滚动条一直显示
		jsp.setVerticalScrollBarPolicy( JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);
		//this.add(jta,BorderLayout.CENTER);  //不需要重复添加
		this.setBounds(300,300,300,400);
		this.setVisible(true);
		this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		//
	}
	public void init() {
		int count = 0; // 记录登录到该服务器的客户端个数
		try {
			sc = new ServerSocket(9995); // 创建一个ServerSocket对象，端口号为1906
			jta.append("服务器已启动"+'\n');
			while (true) {
				Socket socket=sc.accept();
				new ThreadServer(socket,this).start();
			}
		}
		catch (Exception e) {
			// TODO: handle exception
			e.printStackTrace();
		}

	}

	public static void main(String[] args) throws IOException{
		new Server().init();
	}
}

class ThreadServer extends Thread {
	private Socket ts;
	private Server tsr;
	ThreadServer(){};
	ThreadServer(Socket s,Server sr)
	{
		this.ts = s;
		this.tsr=sr;
	}
	public void run() {

		try {
			while(true)
			{
				DataInputStream dis = new DataInputStream(ts.getInputStream());
				String message=dis.readUTF();
				if(message.endsWith("：登入成功")) {
					message.replaceAll("：登入成功", "");
					tsr.socketsMaps.put(ts,message);
				}
				tsr.jta.append(message+'\n');
				Set<Socket> sockets = tsr.socketsMaps.keySet();
				for(Socket tts : sockets) {
					DataOutputStream dos = new DataOutputStream(tts.getOutputStream());
					dos.writeUTF(message);
					dos.flush();
				}
			}
		}
		catch (IOException e2) {
			// TODO: handle exception
			e2.printStackTrace();
		}
	}
}

