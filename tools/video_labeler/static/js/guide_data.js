/**
 * KTTC_FC - Sổ Tay Quy Chuẩn Gán Nhãn & Tham Chiếu Hình Ảnh Thao Tác
 * Cập nhật chuẩn theo QUY_CHUAN_GAN_NHAN_KTTC_FC.html (v2.0 Visual)
 * Dùng cho Giao diện Video Labeler (Right Panel - Dynamic Spec Companion & Center Quick Guide)
 */

const GUIDE_STEPS = {
  "B1": {
    "id": "B1",
    "step_num": "B1",
    "name": "Tháo Đầu Fast Connector (FC)",
    "duration": "⏱️ ~2.3 giây (00:13.67 ➔ 00:15.98)",
    "sample_range": "00:13.67 ➔ 00:15.98 (Key: 00:15.11)",
    "tool": "fast_connector",
    "tool_name": "Đầu Fast Connector",
    "tool_detail": "Tay không + Đầu Fast Connector (thân đen, vỏ bảo vệ xanh lá, chuôi ốc ren đen).",
    "criteria": "Đầu FC được tách thành 3 phần rõ ràng: Vỏ xanh, Thân FC đen, và Chuôi ốc đen để sẵn trên bàn.",
    "warning": "Một số thợ làm B2 (cắt dây) trước B1. Vẫn gán đúng B1 lúc thợ tháo FC, không bị gò bó thứ tự.",
    "color": "#2563eb",
    "badge_class": "bg-blue-600 text-white",
    "moments": {
      "S": "Khoảnh khắc KTV cầm FC chuẩn bị vặn",
      "Key": "Khoảnh khắc KTV đang vặn FC",
      "E": "Khoảnh khắc 2 phần của FC tách rời nhau ra"
    },
    "images": {
      "start": {
        "file": "B1_1.jpg",
        "url": "/static/img/B1_1.jpg",
        "label": "Start",
        "time": "00:13.67",
        "frame": 410,
        "desc": "Start: 00:13.67 (KTV cầm FC chuẩn bị vặn)"
      },
      "key": {
        "file": "B1_2.jpg",
        "url": "/static/img/B1_2.jpg",
        "label": "Key",
        "time": "00:15.11",
        "frame": 453,
        "desc": "⭐ KEY: 00:15.11 (KTV đang vặn FC)"
      },
      "end": {
        "file": "B1_3.jpg",
        "url": "/static/img/B1_3.jpg",
        "label": "End",
        "time": "00:15.98",
        "frame": 479,
        "desc": "End: 00:15.98 (2 phần của FC tách rời nhau ra)"
      }
    }
  },

  "B2": {
    "id": "B2",
    "step_num": "B2",
    "name": "Tách & Cắt Bỏ Dây Treo Kim Loại",
    "duration": "⏱️ ~7.7 giây (00:03.40 ➔ 00:11.07)",
    "sample_range": "00:03.40 ➔ 00:11.07 (Key: 00:08.70)",
    "tool": "kem_cat",
    "tool_name": "Kềm cắt cáp cơ khí",
    "tool_detail": "Kềm cắt cáp cơ khí (cán bọc cao su đỏ-xanh hoặc vàng, 2 lưỡi vát sắc nhọn).",
    "criteria": "Dây thép gia cường bị bấm đứt rời khỏi thân cáp; đầu cáp chỉ còn phần dẹp chứa sợi quang.",
    "warning": "Kềm cắt B2 khác hẳn kềm tuốt vỏ B4 (xanh lá) và kềm tuốt sợi B5 (xanh dương nhỏ). Thợ có thể làm B2 trước B1.",
    "color": "#dc2626",
    "badge_class": "bg-red-600 text-white",
    "moments": {
      "S": "Khoảnh khắc KTV dùng kiềm cắt cắt tách đôi đầu lõi và treo",
      "Key": "Khoảnh khắc KTV đang kéo tách đôi lõi và dây treo",
      "E": "KTV bấm cắt dây treo"
    },
    "images": {
      "start": {
        "file": "B2_1.jpg",
        "url": "/static/img/B2_1.jpg",
        "label": "Start",
        "time": "00:03.40",
        "frame": 102,
        "desc": "Start: 00:03.40 (KTV dùng kiềm cắt cắt tách đôi đầu lõi và treo)"
      },
      "key": {
        "file": "B2_2.jpg",
        "url": "/static/img/B2_2.jpg",
        "label": "Key",
        "time": "00:08.70",
        "frame": 261,
        "desc": "⭐ KEY: 00:08.70 (KTV đang kéo tách đôi lõi và dây treo)"
      },
      "end": {
        "file": "B2_3.jpg",
        "url": "/static/img/B2_3.jpg",
        "label": "End",
        "time": "00:11.07",
        "frame": 332,
        "desc": "End: 00:11.07 (KTV bấm cắt dây treo)"
      }
    }
  },

  "B3": {
    "id": "B3",
    "step_num": "B3",
    "name": "Luồn Cáp Vào Chuôi Ốc Chốt",
    "duration": "⏱️ ~1.5 giây (00:17.48 ➔ 00:18.98)",
    "sample_range": "00:17.48 ➔ 00:18.98 (Key: 00:17.94)",
    "tool": "chuoi_oc_fc",
    "tool_name": "Chuôi ốc ren đen FC",
    "tool_detail": "Tay cầm chuôi ốc ren đen FC và đầu cáp quang vừa cắt ở B2.",
    "criteria": "Đầu cáp chui lọt hẳn qua ống chuôi ốc; chuôi ốc trượt lùi về phía sau trên dây cáp.",
    "warning": "Nếu thợ quên không luồn ốc trước khi tuốt vỏ B4/B5 thì KHÔNG gán B3 (đánh dấu lỗi quy trình).",
    "color": "#d97706",
    "badge_class": "bg-amber-600 text-white",
    "moments": {
      "S": "Khoảnh khắc đuôi FC sắp chạm vào dây",
      "Key": "Khoảnh khắc đuôi FC được luồng hoàn toàn vào dây",
      "E": "Khoảnh khắc đuôi FC được luồng xuống sâu, cách đầu dây khoảng dài"
    },
    "images": {
      "start": {
        "file": "B3_1.jpg",
        "url": "/static/img/B3_1.jpg",
        "label": "Start",
        "time": "00:17.48",
        "frame": 524,
        "desc": "Start: 00:17.48 (Đuôi FC sắp chạm vào dây)"
      },
      "key": {
        "file": "B3_2.jpg",
        "url": "/static/img/B3_2.jpg",
        "label": "Key",
        "time": "00:17.94",
        "frame": 538,
        "desc": "⭐ KEY: 00:17.94 (Đuôi FC được luồng hoàn toàn vào dây)"
      },
      "end": {
        "file": "B3_3.jpg",
        "url": "/static/img/B3_3.jpg",
        "label": "End",
        "time": "00:18.98",
        "frame": 569,
        "desc": "End: 00:18.98 (Đuôi FC được luồng xuống sâu, cách đầu dây khoảng dài)"
      }
    }
  },

  "B4": {
    "id": "B4",
    "step_num": "B4",
    "name": "Tuốt Vỏ Ngoài Cáp Phẳng FTTH",
    "duration": "⏱️ ~4.2 giây (00:20.41 ➔ 00:24.58)",
    "sample_range": "00:20.41 ➔ 00:24.58 (Key: 00:24.05)",
    "tool": "kem_tuot_vo_ftth",
    "tool_name": "Kềm tuốt vỏ cáp FTTH màu xanh lá",
    "tool_detail": "Kềm tuốt vỏ cáp FTTH màu xanh lá cây (kẹp ép phẳng) + Thước cữ đo đen.",
    "criteria": "Lớp vỏ nhựa đen ngoài cùng bị tuột ra, lộ đoạn sợi bọc màu dài khoảng 40–50mm được đo chuẩn cữ.",
    "warning": "Kềm B4 có thân to màu xanh lá. Đừng nhầm với kềm tuốt sợi nhỏ cán xanh dương của B5.",
    "color": "#059669",
    "badge_class": "bg-emerald-600 text-white",
    "moments": {
      "S": "Khoảnh khắc dây treo chạm kiềm tách",
      "Key": "Khoảnh khắc KTV dùng sức bấm kiềm tách",
      "E": "Khoảnh khắc lộ ra lõi dây quang"
    },
    "images": {
      "start": {
        "file": "B4_1.jpg",
        "url": "/static/img/B4_1.jpg",
        "label": "Start",
        "time": "00:20.41",
        "frame": 612,
        "desc": "Start: 00:20.41 (Dây treo chạm kiềm tách)"
      },
      "key": {
        "file": "B4_2.jpg",
        "url": "/static/img/B4_2.jpg",
        "label": "Key",
        "time": "00:24.05",
        "frame": 721,
        "desc": "⭐ KEY: 00:24.05 (KTV dùng sức bấm kiềm tách)"
      },
      "end": {
        "file": "B4_3.jpg",
        "url": "/static/img/B4_3.jpg",
        "label": "End",
        "time": "00:24.58",
        "frame": 737,
        "desc": "End: 00:24.58 (Lộ ra lõi dây quang)"
      }
    }
  },

  "B5": {
    "id": "B5",
    "step_num": "B5",
    "name": "Tuốt Lớp Vỏ Màu Sợi Quang",
    "duration": "⏱️ ~5.2 giây (00:29.42 ➔ 00:34.65)",
    "sample_range": "00:29.42 ➔ 00:34.65 (Key: 00:33.28)",
    "tool": "kem_tuot_soi_3lo",
    "tool_name": "Kềm tuốt sợi 3 lỗ cán xanh dương",
    "tool_detail": "Kềm tuốt sợi 3 lỗ cán xanh dương (mũi kềm có các lỗ tròn nhỏ chuyên tuốt sợi 250µm).",
    "criteria": "Lớp vỏ màu tuột ra, để lộ sợi thủy tinh trong suốt mảnh như sợi tóc ở đầu sợi cáp.",
    "warning": "Động tác tuốt diễn ra rất dứt khoát trong 1-2 giây. Bắt đúng frame sợi vỏ màu bị kéo tuột ra.",
    "color": "#0891b2",
    "badge_class": "bg-cyan-600 text-white",
    "moments": {
      "S": "Khoảnh khắc dây quang được đặt hoàn toàn vào thước đo",
      "Key": "Khoảnh khắc KTV đang dùng lực bấm kiềm tuốt tuốt lõi quang",
      "E": "Khoảnh khắc kiềm tuốt rời khỏi dây quang"
    },
    "images": {
      "start": {
        "file": "B5_1.jpg",
        "url": "/static/img/B5_1.jpg",
        "label": "Start",
        "time": "00:29.42",
        "frame": 882,
        "desc": "Start: 00:29.42 (Dây quang được đặt hoàn toàn vào thước đo)"
      },
      "key": {
        "file": "B5_2.jpg",
        "url": "/static/img/B5_2.jpg",
        "label": "Key",
        "time": "00:33.28",
        "frame": 998,
        "desc": "⭐ KEY: 00:33.28 (KTV đang dùng lực bấm kiềm tuốt tuốt lõi quang)"
      },
      "end": {
        "file": "B5_3.jpg",
        "url": "/static/img/B5_3.jpg",
        "label": "End",
        "time": "00:34.65",
        "frame": 1039,
        "desc": "End: 00:34.65 (Kiềm tuốt rời khỏi dây quang)"
      }
    }
  },

  "B6a": {
    "id": "B6a",
    "step_num": "B6a",
    "name": "Vệ Sinh Sợi Quang Bằng Cồn (Lau Cồn)",
    "duration": "⏱️ ~8.7 giây (01:28.84 ➔ 01:37.53)",
    "sample_range": "01:28.84 ➔ 01:37.53 (Key: 01:32.46)",
    "tool": "chai_con_giay_lau",
    "tool_name": "Chai cồn nhấn + Giấy lau không bụi",
    "tool_detail": "Chai cồn nhấn (lọ nhựa trong suốt) + Khăn giấy lau không bụi (Kimwipes).",
    "criteria": "Kẹp giấy cồn vuốt dọc sợi thủy tinh 1-2 lần làm sạch bụi bẩn.",
    "warning": "Tách thành nhãn riêng với B6b vì dùng công cụ khác và có thể làm nhiều lần.",
    "color": "#4f46e5",
    "badge_class": "bg-indigo-600 text-white",
    "moments": {
      "S": "Khoảnh khắc KTV cho cồn vào khăn giấy",
      "Key": "Khoảnh khắc khăn giấy chạm vào sợi quang",
      "E": "Khoảnh khắc khăn giấy được KTV để ra chỗ khác"
    },
    "images": {
      "start": {
        "file": "B6a_1.jpg",
        "url": "/static/img/B6a_1.jpg",
        "label": "Start",
        "time": "01:28.84",
        "frame": 2627,
        "desc": "Start: 01:28.84 (KTV cho cồn vào khăn giấy)"
      },
      "key": {
        "file": "B6a_2.jpg",
        "url": "/static/img/B6a_2.jpg",
        "label": "Key",
        "time": "01:32.46",
        "frame": 2734,
        "desc": "⭐ KEY: 01:32.46 (Khăn giấy chạm vào sợi quang)"
      },
      "end": {
        "file": "B6a_3.jpg",
        "url": "/static/img/B6a_3.jpg",
        "label": "End",
        "time": "01:37.53",
        "frame": 2884,
        "desc": "End: 01:37.53 (Khăn giấy được KTV để ra chỗ khác)"
      }
    }
  },

  "B6b": {
    "id": "B6b",
    "step_num": "B6b",
    "name": "Cắt Sợi Bằng Dao Cắt Chính Xác",
    "duration": "⏱️ ~5.2 giây (01:41.42 ➔ 01:46.66)",
    "sample_range": "01:41.42 ➔ 01:46.66 (Key: 01:42.27)",
    "tool": "dao_cat_quang",
    "tool_name": "Dao cắt sợi quang (Cleaver)",
    "tool_detail": "Dao cắt sợi quang chuyên dụng (Fiber Cleaver) màu đen đặt cố định trên bàn.",
    "criteria": "Đặt sợi vào rãnh cữ, dập nắp dao và cắt ngọt đầu sợi 90 độ.",
    "warning": "Dao cắt cần đặt trên mặt phẳng vững chãi, không cầm lơ lửng trên tay.",
    "color": "#7c3aed",
    "badge_class": "bg-purple-600 text-white",
    "moments": {
      "S": "Khoảnh khắc KTV đặt FC + thước đo vào kéo cắt",
      "Key": "Khoảnh khắc đóng nắp kéo cắt, cắt lõi quang",
      "E": "Khoảnh khắc FC + thước đo tách rời khỏi kéo cắt"
    },
    "images": {
      "start": {
        "file": "B6b_1.jpg",
        "url": "/static/img/B6b_1.jpg",
        "label": "Start",
        "time": "01:41.42",
        "frame": 2999,
        "desc": "Start: 01:41.42 (KTV đặt FC + thước đo vào kéo cắt)"
      },
      "key": {
        "file": "B6b_2.jpg",
        "url": "/static/img/B6b_2.jpg",
        "label": "Key",
        "time": "01:42.27",
        "frame": 3024,
        "desc": "⭐ KEY: 01:42.27 (Đóng nắp kéo cắt, cắt lõi quang)"
      },
      "end": {
        "file": "B6b_3.jpg",
        "url": "/static/img/B6b_3.jpg",
        "label": "End",
        "time": "01:46.66",
        "frame": 3154,
        "desc": "End: 01:46.66 (FC + thước đo tách rời khỏi kéo cắt)"
      }
    }
  },

  "B7": {
    "id": "B7",
    "step_num": "B7",
    "name": "Luồn Sợi Vào Thân Fast Connector",
    "duration": "⏱️ ~14.7 giây (01:52.21 ➔ 02:06.96)",
    "sample_range": "01:52.21 ➔ 02:06.96 (Key: 01:57.35)",
    "tool": "than_fc",
    "tool_name": "Thân Fast Connector đen",
    "tool_detail": "Thân Fast Connector đen (có đầu sứ trắng ferrule) và sợi quang vừa cắt phẳng ở B6b.",
    "criteria": "Sợi cắm kịch đáy chạm gel, thân sợi cáp hơi cong nhẹ một cung vòm (độ uốn vi sai bảo đảm tiếp xúc).",
    "warning": "Frame Key_Time là frame thấy rõ nhất sợi cáp hơi oằn cong nhẹ trước khi siết chuôi ốc.",
    "color": "#9333ea",
    "badge_class": "bg-violet-600 text-white",
    "moments": {
      "S": "Khoảnh khắc KTV cầm cả đầu FC và dây quang",
      "Key": "Khoảnh khắc dây quang chạm vào đầu FC",
      "E": "Khoảnh khắc dây quang nằm hẳn trong đầu FC"
    },
    "images": {
      "start": {
        "file": "B7_1.jpg",
        "url": "/static/img/B7_1.jpg",
        "label": "Start",
        "time": "01:52.21",
        "frame": 3318,
        "desc": "Start: 01:52.21 (KTV cầm cả đầu FC và dây quang)"
      },
      "key": {
        "file": "B7_2.jpg",
        "url": "/static/img/B7_2.jpg",
        "label": "Key",
        "time": "01:57.35",
        "frame": 3470,
        "desc": "⭐ KEY: 01:57.35 (Dây quang chạm vào đầu FC)"
      },
      "end": {
        "file": "B7_3.jpg",
        "url": "/static/img/B7_3.jpg",
        "label": "End",
        "time": "02:06.96",
        "frame": 3754,
        "desc": "End: 02:06.96 (Dây quang nằm hẳn trong đầu FC)"
      }
    }
  },

  "B8": {
    "id": "B8",
    "step_num": "B8",
    "name": "Vặn Siết Chuôi Ốc Chốt Cáp",
    "duration": "⏱️ ~5.4 giây (02:07.70 ➔ 02:13.14)",
    "sample_range": "02:07.70 ➔ 02:13.14 (Key: 02:09.46)",
    "tool": "chuoi_oc_ren",
    "tool_name": "Chuôi ốc ren đen + Thân FC",
    "tool_detail": "Tay xoay vặn chuôi ốc ren đen vào đuôi thân Fast Connector.",
    "criteria": "Ren ốc được vặn siết chặt khít vào thân FC, kẹp cứng vỏ cáp không bị tuột khi kéo nhẹ.",
    "warning": "Bước này diễn ra trước khi đóng nắp vỏ xanh B9. Chuôi ốc đen phải được vặn hết ren.",
    "color": "#0d9488",
    "badge_class": "bg-teal-600 text-white",
    "moments": {
      "S": "Khoảnh khắc KTV kéo đuôi FC lên sát đầu FC chuẩn bị vặn",
      "Key": "Khoảnh khắc KTV vặn FC",
      "E": "Khoảnh khắc KTV dừng vặn FC"
    },
    "images": {
      "start": {
        "file": "B8_1.jpg",
        "url": "/static/img/B8_1.jpg",
        "label": "Start",
        "time": "02:07.70",
        "frame": 3776,
        "desc": "Start: 02:07.70 (KTV kéo đuôi FC lên sát đầu FC chuẩn bị vặn)"
      },
      "key": {
        "file": "B8_2.jpg",
        "url": "/static/img/B8_2.jpg",
        "label": "Key",
        "time": "02:09.46",
        "frame": 3828,
        "desc": "⭐ KEY: 02:09.46 (KTV vặn FC)"
      },
      "end": {
        "file": "B8_3.jpg",
        "url": "/static/img/B8_3.jpg",
        "label": "End",
        "time": "02:13.14",
        "frame": 3937,
        "desc": "End: 02:13.14 (KTV dừng vặn FC)"
      }
    }
  },

  "B9": {
    "id": "B9",
    "step_num": "B9",
    "name": "Khóa Chốt & Đóng Nắp Vỏ Hoàn Thiện",
    "duration": "⏱️ ~0.4 giây (02:13.75 ➔ 02:14.19)",
    "sample_range": "02:13.75 ➔ 02:14.19 (Key: 02:14.09)",
    "tool": "vo_xanh_fc",
    "tool_name": "Vỏ bảo vệ màu xanh lá FC",
    "tool_detail": "Vỏ bảo vệ màu xanh lá FC (tháo ở B1) và thân đầu nối FC đã siết ốc.",
    "criteria": "Vỏ xanh trượt khớp ngàm vào thân FC, khóa chốt an toàn; thợ giơ đầu FC hoàn thiện lên kiểm tra.",
    "warning": "Mốc End của B9 cũng là mốc kết thúc toàn bộ quy trình thi công của video.",
    "color": "#16a34a",
    "badge_class": "bg-green-600 text-white",
    "moments": {
      "S": "Khoảnh khắc tay KTV chạm nắp FC",
      "Key": "Khoảnh khắc KTV dùng lực gỡ nắp FC",
      "E": "Khoảnh khắc nắp FC rời hẳn ra khỏi FC"
    },
    "images": {
      "start": {
        "file": "B9_1.jpg",
        "url": "/static/img/B9_1.jpg",
        "label": "Start",
        "time": "02:13.75",
        "frame": 3955,
        "desc": "Start: 02:13.75 (Tay KTV chạm nắp FC)"
      },
      "key": {
        "file": "B9_2.jpg",
        "url": "/static/img/B9_2.jpg",
        "label": "Key",
        "time": "02:14.09",
        "frame": 3965,
        "desc": "⭐ KEY: 02:14.09 (KTV dùng lực gỡ nắp FC)"
      },
      "end": {
        "file": "B9_3.jpg",
        "url": "/static/img/B9_3.jpg",
        "label": "End",
        "time": "02:14.19",
        "frame": 3968,
        "desc": "End: 02:14.19 (Nắp FC rời hẳn ra khỏi FC)"
      }
    }
  },

  "B0": {
    "id": "B0",
    "step_num": "B0",
    "name": "Trạng Thái Nghỉ / Chuyển Tiếp (Transition / Idle)",
    "duration": "Tự động điền mọi khoảng trống (2s - 54s)",
    "sample_range": "Mọi frame không thuộc các bước thao tác chính thức",
    "tool": "none",
    "tool_name": "Không dùng dụng cụ",
    "tool_detail": "Thao tác phụ: vuốt thẳng cuộn cáp, ngồi chuẩn bị đồ nghề, tìm dụng cụ, đổi góc quay.",
    "criteria": "Mọi frame trong video không thuộc 10 hành động trên đều là B0.",
    "warning": "Khoảng nghỉ tự động điền, giúp AI học nhận biết 'lúc thợ không làm gì', triệt tiêu cảnh báo ảo.",
    "color": "#64748b",
    "badge_class": "bg-slate-500 text-white",
    "moments": {
      "S": "Bắt đầu khoảng nghỉ/chuyển tiếp",
      "Key": "Chuyển tiếp giữa các bước",
      "E": "Kết thúc khoảng nghỉ"
    },
    "images": {
      "transition": {
        "file": "b0_transition.jpg",
        "url": "/static/img/b0_transition.jpg",
        "label": "Transition",
        "desc": "B0: Nghỉ / Chuyển tiếp / Chuẩn bị đồ nghề"
      },
      "start": {
        "file": "b0_transition.jpg",
        "url": "/static/img/b0_transition.jpg",
        "label": "Transition",
        "desc": "B0: Nghỉ / Chuyển tiếp"
      },
      "key": {
        "file": "b0_transition.jpg",
        "url": "/static/img/b0_transition.jpg",
        "label": "Transition",
        "desc": "B0: Nghỉ / Chuyển tiếp"
      },
      "end": {
        "file": "b0_transition.jpg",
        "url": "/static/img/b0_transition.jpg",
        "label": "Transition",
        "desc": "B0: Nghỉ / Chuyển tiếp"
      }
    }
  }
};

// Aliases for compatibility between naming conventions
GUIDE_STEPS["B6_clean"] = GUIDE_STEPS["B6a"];
GUIDE_STEPS["B6_cut"] = GUIDE_STEPS["B6b"];

// Standard sequential list of action steps
const GUIDE_STEPS_LIST = [
  "B1", "B2", "B3", "B4", "B5", "B6a", "B6b", "B7", "B8", "B9"
];

/**
 * Get step guide by label or alias
 * @param {string} stepId - e.g. "B1", "B6a", "B6_clean"
 * @returns {object|null}
 */
function getGuideStep(stepId) {
  if (!stepId) return null;
  const normalized = String(stepId).trim();
  return GUIDE_STEPS[normalized] || null;
}

// Support Node.js / Jest / CommonJS environments
if (typeof module !== "undefined" && module.exports) {
  module.exports = { GUIDE_STEPS, GUIDE_STEPS_LIST, getGuideStep };
}

// Support Browser globals
if (typeof window !== "undefined") {
  window.GUIDE_STEPS = GUIDE_STEPS;
  window.GUIDE_STEPS_LIST = GUIDE_STEPS_LIST;
  window.getGuideStep = getGuideStep;
}
