package com.huawei.visualPanel;

import java.awt.BorderLayout;

import java.awt.Container;
import java.awt.FlowLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.net.ServerSocket;
import java.net.Socket;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JPasswordField;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.JTextField;

import java.io.*;
class Login extends JFrame implements ActionListener{
	//用户名
	JPanel jp1=new JPanel();
	JLabel jl1=new JLabel("用户名");
	public JTextField jtf1=new JTextField(15);
	//密码
	JPanel jp2=new JPanel();
	JLabel jl2=new JLabel("密码");
	JPasswordField jpf2 = new JPasswordField(15);
	//登入取消按钮
	JPanel jp3=new JPanel();
	JButton jbt1=new JButton("登入");
	JButton jbt2=new JButton("取消");

	public Login() {
		// TODO 自动生成的构造函数存根
		this.setTitle("客服端登入窗口");
		Container con =this.getContentPane();
		con.setLayout(new FlowLayout());
		//用户名
		jp1.add(jl1);
		jp1.add(jtf1);
		jtf1.addActionListener(this);
		//密码
		jpf2.setEchoChar('*');  //用*显示密码框输入的数据
		jp2.add(jl2);
		jp2.add(jpf2);
		jpf2.addActionListener(this);
		//登入取消按钮
		jp3.add(jbt1);
		jp3.add(jbt2);
		//添加到当前窗口容器
		con.add(jp1);
		con.add(jp2);
		con.add(jp3);
		this.setSize(500, 300);    //设置窗体大小
		setLocationRelativeTo(null); //设置窗口居中
		this.setResizable(false);  //窗体大小设置为不可改
		this.setVisible(true);  //窗体设置为可见
		this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		//光标聚焦在用户框中
		jtf1.requestFocus();
		//为登入按钮添加监听器
		jbt1.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO 自动生成的方法存根
				String name=jtf1.getText();
				String password=new String(jpf2.getPassword()); //获取密码框中的密码
				try {
					if(password.equals("123")) {
						setVisible(false);
						new Client(jtf1.getText());
					}
					else {
						JOptionPane.showConfirmDialog(null, "用户名或密码错误！",
								"提示",JOptionPane.DEFAULT_OPTION);
					}
				} catch (Exception e2) {
					// TODO: handle exception
					e2.printStackTrace();
				}
			}
		});
		jbt2.addActionListener(new ActionListener() { //为取消按钮添加监听器

			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO 自动生成的方法存根
				try {
					setVisible(false);
				} catch (Exception e2) {
					// TODO: handle exception
				}
			}
		});
	}
	//移动光标聚集
	public void actionPerformed(ActionEvent e) {
		Object o=e.getSource();
		if(o==jtf1) {
			jpf2.requestFocus();
		}
	}
}

public class Client extends JFrame  {
	public DataOutputStream dos=null;
	public DataInputStream dis=null;
	public Socket s=null;
	public ServerSocket sc=null;
	//
	public JTextArea jta=new JTextArea(10,20);
	public JTextField jtf=new JTextField(20);
	public JScrollPane jsp = new JScrollPane(jta);
	static final String CONNSTR="127.0.0.1";
	public String ClientName="";

	//构造函数初始化
	Client(String tClientName) throws IOException{
		ClientName=tClientName;
		this.setTitle("客服端："+ClientName);
		jta.setEditable(false); //文本显示框不可编辑
		this.add(jtf,BorderLayout.SOUTH);
		this.add(jsp,BorderLayout.CENTER);
		//默认的设置是超过文本框才会显示滚动条,以下设置让滚动条一直显示
		jsp.setVerticalScrollBarPolicy( JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);
		//连接服务器

		try {
			s=new Socket(CONNSTR,9995);
			new ThreadClient(s,this).start();
		} catch (Exception e) {
			// TODO: handle exception
			e.printStackTrace();
			JOptionPane.showConfirmDialog(null, "用户连接服务器失败",
					"提示",JOptionPane.DEFAULT_OPTION);
		}
		//发送登入信息到服务器
		String firstStr="\""+ClientName+"\"："+"登入成功";
		DataOutputStream firstdataOutputStream = new DataOutputStream(s.getOutputStream());
		//发送用户名到服务端
		firstdataOutputStream.writeUTF(firstStr);
		firstdataOutputStream.flush();
		//
		this.setBounds(300,300,300,400);
		//this.setSize(500, 300);    //设置窗体大小
		setLocationRelativeTo(null); //设置窗口居中
		this.setVisible(true);  //窗体设置为可见
		this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		jtf.requestFocus();
		//

		jtf.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO 自动生成的方法存根
				String str=jtf.getText();
				try {
					if(str.length()>0) {
						str="\""+ClientName+"\"："+str;
						sendMessage(str, s);
						jtf.setText("");
					}
				} catch (Exception e2) {
					// TODO: handle exception
					e2.printStackTrace();
					str="\""+ClientName+"\":"+"已退出";
					sendMessage(str,s);
				}

			}
		});
	}
	//客服端发送信息到服务器
	protected void sendMessage(String message, Socket s) {
		try {
			DataOutputStream dos = new DataOutputStream(s.getOutputStream());
			dos.writeUTF(message);
			dos.flush();
		} catch (Exception e) {
			// TODO: handle exception
			e.printStackTrace();
		}
	}
	public static void main(String[] args) {
		new Login();
	}
}
//定义线程类,读取服务器发送的信息
class ThreadClient extends Thread {
	private Socket s;
	private Client clientChat;

	ThreadClient(Socket socket, Client clientChat) {
		this.s = socket;
		this.clientChat = clientChat;
	}
	@Override
	public void run() {
		String message;
		try {
			while (true) {
				DataInputStream DataInputStream = new DataInputStream(s.getInputStream());
				message = DataInputStream.readUTF();
				clientChat.jtf.setText("");
				clientChat.jta.append(message+"\n");
			}
		}
		catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			message="\""+clientChat.ClientName+"\":"+"已退出";
			clientChat.sendMessage(message,s);
		}
	}
}

