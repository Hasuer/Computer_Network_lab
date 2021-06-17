package com.huawei.chat01;

import java.io.*;
import java.net.Socket;

public class Send implements Runnable {

	// 输入流
	private DataInputStream dis;
	// 输出流
	private DataOutputStream dos;
	// 客户端名称
	private String name;
	// 控制线程
	private boolean isRunning = true;

	public Send(Socket client, String name) {
		try {
			dis = new DataInputStream(client.getInputStream());
			dos = new DataOutputStream(client.getOutputStream());
			this.name = name;
			send(this.name); // 把自己的名字发给服务端
		} catch (IOException e) {
			e.printStackTrace();
			isRunning = false;
			Util.closeAll(dos, dis);
		}
	}

	/**
	 * 从控制台接收数据并发送数据
	 */
	public void send(String msg) {
		try {
			if (msg != null && !"".equals(msg)) {
				dos.writeUTF(msg);
				dos.flush(); // 强制刷新
			}
		} catch (IOException e) {
			e.printStackTrace();
			isRunning = false;
			Util.closeAll(dos, dis);
		}
	}

	// 从控制台接收数据
	private String getMsgFromConsole() {
		try {
			return dis.readUTF();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return "";
	}

	@Override
	public void run() {
		while (isRunning) {
			send(getMsgFromConsole());
		}
	}
}
