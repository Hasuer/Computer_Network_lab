package com.huawei.chat01;

import org.omg.CosNaming.BindingIterator;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;

public class ClientChat extends JFrame {
    private JTextArea ta = new JTextArea(10, 20); //显示的地方
    private JTextField tf = new JTextField(20); //输入的地方

    public ClientChat() throws HeadlessException {

    }

    public void init() {
        this.setTitle("客户端窗口");
        this.add(ta, BorderLayout.CENTER);
        this.add(tf, BorderLayout.SOUTH);
        this.setBounds(200, 200, 500, 600);
        this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        tf.addActionListener(new AbstractAction() {
            //监听, tf中的消息显示在tf上
            @Override
            public void actionPerformed(ActionEvent e) {
                String strSend = tf.getText();
                if(strSend.trim().length() == 0){
                    return ;
                }
                ta.append(strSend + '\n');
                tf.setText("");
            }
        });
        ta.setEditable(false);//显示窗口不可编辑
        tf.requestFocus();//光标位置设置
        this.setVisible(true);
    }

    public static void main(String[] args) {
        ClientChat cc = new ClientChat();
        cc.init();
    }
}
